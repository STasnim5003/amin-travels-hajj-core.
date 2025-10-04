from datetime import datetime

import pandas as pd
import psycopg2.extras as extras
from dotenv import load_dotenv

from app.core.utils.data_clean import normalize_entry, normalize_nid

load_dotenv()


def save_new_preregistered_data(df_pilgrims, df_preregistered, conn):
    try:
        df_preregistered = df_preregistered.rename(
            columns={
                "Tracking ID": "tracking_id",
                "Serial No": "serial_no",
                "NID": "nid"
            }
        )

        df_pilgrims["tracking_id"] = df_pilgrims["tracking_id"].fillna("").astype(str)
        df_preregistered["tracking_id"] = df_preregistered["tracking_id"].fillna("").astype(str)

        df_new_tracking = df_preregistered[~df_preregistered["tracking_id"].isin(df_pilgrims["tracking_id"])]
        if df_new_tracking.empty:
            print("No new data to insert.")
            return

        df_cleaned_list = df_new_tracking.apply(lambda row: normalize_entry(row), axis=1)
        df_cleaned = pd.DataFrame(df_cleaned_list.tolist())

        table_name = "core.pilgrim_data"

        columns = list(df_cleaned.columns)
        values = [[row[col] for col in columns] for _, row in df_cleaned.iterrows()]

        insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES %s
        """

        with conn.cursor() as cur:
            extras.execute_values(cur, insert_query, values)
            conn.commit()

        print(f"{len(df_cleaned)} rows inserted.")


    except Exception as e:
        print("Error loading data:", e)


def registered_data(df_registered, conn):
    try:
        table_name = "core.pilgrim_data"
        columns_to_update = ["passport_no", "passport_expiry_date", "payment_status"]

        def format_date_ddmonyyyy(date_str):
            if pd.isna(date_str):
                return None
            try:
                dt = pd.to_datetime(date_str)
                return dt.strftime("%d-%b-%Y")
            except:
                return None

        df_registered["passport_expiry_date"] = df_registered["passport_expiry_date"].apply(format_date_ddmonyyyy)

        columns_to_update += ["registration_status", "updated_by", "updated_at"]

        update_query = f"""
        UPDATE {table_name}
        SET {', '.join([f"{col} = %s" for col in columns_to_update])}
        WHERE tracking_id = %s;
        """

        update_at = datetime.now()

        with conn.cursor() as cur:
            for _, row in df_registered.iterrows():
                values = [
                             row["passport_no"],
                             row["passport_expiry_date"],
                             row["payment_status"],
                             "REGISTERED",  # registration_status
                             "script",  # updated_by
                             update_at  # updated_at
                         ] + [row["tracking_id"]]  # WHERE clause
                cur.execute(update_query, values)

            conn.commit()
        print(f"Updated {len(df_registered)} rows based on tracking_id.")

    except Exception as e:
        print("Error loading data:", e)


def move_walkin_to_preregistration(df_pilgrims, df_preregistered, conn):
    try:
        df_preregistered = df_preregistered.rename(
            columns={
                "NID": "nid",
                "Serial No": "serial_no",
                "Tracking ID": "tracking_id"
            }
        )

        # Make sure nid is
        df_pilgrims["nid"] = df_pilgrims["nid"].apply(normalize_nid)
        df_preregistered["nid"] = df_preregistered["nid"].apply(normalize_nid)

        walkin_nids = df_pilgrims.loc[
            (df_pilgrims["registration_status"] == "WALK_IN"),
            "nid"
        ].unique()

        df_prereg_walkin = df_preregistered[df_preregistered["nid"].isin(walkin_nids)]
        if df_prereg_walkin.empty:
            print("No cleaned data to update.")
            return

        df_cleaned = df_prereg_walkin.apply(lambda row: normalize_entry(row), axis=1)

        if len(df_cleaned) > 0:
            df_cleaned = pd.DataFrame(df_cleaned.tolist())
        else:
            expected_columns = [
                "name_bn", "name_en", "father_name", "spouse_name", "occupation", "nid", "voucher", "type",
                "listed_in", "mother_name", "date_of_birth", "gender", "management", "mobile_no",
                "passport_address",
                "present_address", "permanent_address", "tracking_id", "serial_no", "group_name", "hajj_year",
                "is_assigned", "registration_status", "password", "preliminary_password", "allocation_status",
                "vaccination_center", "nominee_info", "passport_copy", "package_id", "comment_on_package",
                "is_active"
            ]
            df_cleaned = pd.DataFrame(columns=expected_columns)

        # Get list of columns (excluding nid since that's our WHERE key)
        columns = [col for col in df_cleaned.columns if col != "nid"]

        # Build SET part of update query dynamically
        set_clause = ", ".join([f"{col} = %s" for col in columns])

        query = f"""
            UPDATE core.pilgrim_data
            SET {set_clause}
            WHERE nid = %s;
            """

        try:
            with conn.cursor() as cur:
                for _, row in df_cleaned.iterrows():
                    values = [row[col] for col in columns] + [row["nid"]]
                    cur.execute(query, values)

            conn.commit()
            print(f"Updated {len(df_cleaned)} rows from walkin to preregistration.")
        except Exception as e:
            conn.rollback()
            print(f"Error while updating: {e}")

    except Exception as e:
        print("Error loading data:", e)


def update_draft_serial_no(df_pilgrims, df_preregistered, conn):
    try:
        draft_df = df_pilgrims.loc[df_pilgrims["serial_no"] == "Draft", ["tracking_id"]]

        if draft_df.empty:
            return
        df_preregistered = df_preregistered.rename(
            columns={
                "NID": "nid",
                "Serial No": "serial_no",
                "Tracking ID": "tracking_id"
            }
        )

        df_preregistered["tracking_id"] = df_preregistered["tracking_id"].astype(str).str.strip()
        draft_tracking_ids = draft_df["tracking_id"].astype(str).str.strip().tolist()

        # Select only rows in preregistered that match draft tracking_ids
        prereg_to_update = df_preregistered[df_preregistered["tracking_id"].isin(draft_tracking_ids)][
            ["tracking_id", "serial_no"]]

        if prereg_to_update.empty:
            print("No preregistered entries match Draft tracking IDs.")
            return

        table_name = "core.pilgrim_data"

        update_query = f"""
        UPDATE {table_name}
        SET serial_no = %s,
            updated_at = %s,
            updated_by = %s
        WHERE tracking_id = %s;
        """

        now = datetime.now()

        with conn.cursor() as cur:
            for _, row in prereg_to_update.iterrows():
                tracking_id = row["tracking_id"]
                new_serial_no = row["serial_no"]
                cur.execute(update_query, [new_serial_no, now, "script", tracking_id])
            conn.commit()
        print("Updated serial_no for matching Draft tracking IDs.")
    except Exception as e:
        print(str(e))


def update_refunded(df_preregistered, conn):
    try:
        df_preregistered = df_preregistered.rename(
            columns={
                "NID": "nid",
                "Serial No": "serial_no",
                "Tracking ID": "tracking_id"
            }
        )

        # Filter rows where serial_no is Refunded
        refunded_df = df_preregistered.loc[df_preregistered["serial_no"] == "Refunded", ["tracking_id"]]
        print(refunded_df)
        if refunded_df.empty:
            print("✅ No Refunded entries found.")
            return

        table_name = "core.pilgrim_data"

        update_query = f"""
        UPDATE {table_name}
        SET serial_no = %s,
            allocation_status = %s,
            updated_at = %s,
            updated_by = %s
        WHERE tracking_id = %s;
        """

        now = datetime.now()

        with conn.cursor() as cur:
            for _, row in refunded_df.iterrows():
                tracking_id = str(row["tracking_id"]).strip()
                cur.execute(update_query, ["Refunded", "REFUNDED", now, "script", tracking_id])
            conn.commit()
            print(f"Updated {len(refunded_df)} refunded entries in DB.")

    except Exception as e:
        print(str(e))
