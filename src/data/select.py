from data.access import connection
from utils.watch import logger

# Log Emoji: 🗄️🔍


def execute_select(query, params=None, fetchone=True):
    # Connect to the database
    conn = connection()
    conn.open()
    # logger.debug("🗄️🔍 Database connection opened")

    # Create a cursor
    cur = conn.conn.cursor()

    # Execute the query
    cur.execute(query, params)
    conn.conn.commit()
    logger.info("🗄️✏️🟢 Query executed and committed")
    # logger.debug(f"🗄️🔍 Executed select query: {query}")
    #   logger.debug(f"🗄️🔍 Query parameters: {params}")

    # Fetch the results if requested
    result = None
    if fetchone:
        result = cur.fetchone() if cur.rowcount > 0 else None
    else:
        result = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    conn.close()
    logger.debug("🗄️🔍 Cursor and connection closed")

    return result


# Queries
def next_tech_url():
    query = """
        SELECT url AS "target",
               id AS "url_id"
        FROM (
          SELECT *
          FROM targets.urls
          WHERE active_main IS TRUE
            AND active_scan_tech IS TRUE
          ORDER BY created_at DESC
          LIMIT 500
        ) AS subquery
        OFFSET floor(random() * 100)
        LIMIT 1;
    """
    result = execute_select(query)
    if result:
        target, url_id = result
        logger.info(f'🗄️🔍 Next Tech Check URL: {target}')
        return target, url_id
    else:
        logger.error(f'🗄️🔍 Unable to Tech Check URL')
        return None, None

def next_axe_url():
    query = """
      WITH random_rows AS (
            SELECT url AS "target",
                   id AS "url_id",
                   ROW_NUMBER() OVER (ORDER BY scanned_at_axe NULLS FIRST, created_at) AS row_num
            FROM targets.urls
            WHERE active_main IS TRUE AND active_scan_axe IS TRUE
            LIMIT 100
            OFFSET floor(random() * 100)
        ), latest_within_5_days AS (
            SELECT url AS "target",
                   id AS "url_id"
            FROM targets.urls
            WHERE active_main IS TRUE AND active_scan_axe IS TRUE
                  AND (scanned_at_axe IS NULL OR scanned_at_axe < NOW() - INTERVAL '5 days')
            ORDER BY scanned_at_axe DESC NULLS LAST
            LIMIT 1
        )
        SELECT "target", "url_id"
        FROM random_rows
        UNION ALL
        SELECT "target", "url_id"
        FROM latest_within_5_days
        WHERE NOT EXISTS (SELECT 1 FROM random_rows)
        LIMIT 1;
   """
    result = execute_select(query)
    if result:
        target, url_id = result
        logger.info(f'Snagged {url_id} : {target}')
        return target, url_id
    else:
        logger.error(f'🗄️🔍 Unable to Get URL - Error: {e}')
        return None, None
