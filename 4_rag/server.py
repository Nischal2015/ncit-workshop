import sqlite3
import logging
from fastmcp import FastMCP, Context

# --- 1. Configure Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)
logger = logging.getLogger("CampusDefenderOps")

# Initialize FastMCP
mcp = FastMCP("CampusDefenderOps")
DB_FILE = "campus.db"


def get_db_connection():
    """Helper to connect to the real database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database {DB_FILE}: {e}")
        raise


@mcp.tool()
async def scan_active_threats(ctx: Context) -> str:
    """Scans the campus database for ACTIVE anomalies and returns their details."""
    logger.info("Tool called: scan_active_threats")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM anomalies WHERE status='ACTIVE'")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            logger.info("Scan complete: No active threats found.")
            await ctx.info("No active threats detected on campus.")
            return "🟢 ALL CLEAR. No active threats detected on campus."

        logger.warning(f"Scan complete: {len(rows)} active threats detected.")
        report = "🔴 ACTIVE THREATS DETECTED:\n"
        for row in rows:
            report += f"- [ID: {row['id']}] {row['type']} at {row['location']} (Danger: {row['danger_level']}/10)\n"
        return report

    except Exception as e:
        logger.error(f"Error executing scan_active_threats: {e}", exc_info=True)
        return "❌ Internal System Error while scanning for threats."


@mcp.tool()
async def deploy_hunter(
    threat_id: int,
    hunter_name: str,
    ctx: Context,
) -> str:
    """
    Dispatches a specific hunter to neutralize a threat.
    Updates the database to mark the threat as 'NEUTRALIZED' and hunter as 'BUSY'.
    """
    logger.info(
        f"Tool called: deploy_hunter (Hunter: {hunter_name}, Threat ID: {threat_id})"
    )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check Hunter Status
        cursor.execute("SELECT status FROM hunters WHERE name = ?", (hunter_name,))
        hunter = cursor.fetchone()

        if not hunter:
            conn.close()
            logger.warning(f"Deployment failed: Hunter '{hunter_name}' not found.")
            return f"❌ ERROR: Hunter '{hunter_name}' not found in registry."

        if hunter["status"] != "AVAILABLE":
            conn.close()
            logger.warning(
                f"Deployment failed: Hunter '{hunter_name}' is {hunter['status']}."
            )
            return f"⚠️ Hunter '{hunter_name}' is currently {hunter['status']} and cannot be deployed."

        # Neutralize Threat
        cursor.execute(
            "UPDATE anomalies SET status='NEUTRALIZED' WHERE id = ?", (threat_id,)
        )
        if cursor.rowcount == 0:
            conn.close()
            logger.warning(f"Deployment failed: Threat ID {threat_id} not found.")
            return f"❌ ERROR: Threat ID {threat_id} not found."

        # Set Hunter to Busy
        cursor.execute(
            "UPDATE hunters SET status='BUSY' WHERE name = ?", (hunter_name,)
        )
        conn.commit()
        conn.close()

        logger.info(f"Mission Success: {hunter_name} neutralized Threat #{threat_id}.")
        await ctx.info(
            f"Hunter '{hunter_name}' has successfully neutralized Threat #{threat_id}."
        )
        return f"🚀 MISSION SUCCESS: {hunter_name} has successfully neutralized Threat #{threat_id}. Database updated."

    except Exception as e:
        logger.error(f"Error executing deploy_hunter: {e}", exc_info=True)
        return "❌ Internal System Error during deployment."


@mcp.tool()
async def recruit_new_hunter(
    name: str,
    major: str,
    equipment: str,
    ctx: Context,
) -> str:
    """Recruits a new student into the hunter database."""
    logger.info(f"Tool called: recruit_new_hunter (Name: {name}, Major: {major})")
    await ctx.info(f"Tool called: recruit_new_hunter (Name: {name}, Major: {major})")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO hunters (name, major, equipment, status) VALUES (?, ?, ?, ?)",
            (name, major, equipment, "AVAILABLE"),
        )
        conn.commit()
        conn.close()

        logger.info(f"Recruitment successful: {name} added to database.")
        await ctx.info(f"New recruit '{name}' has joined the hunter roster.")
        return f"✅ NEW RECRUIT: {name} ({major}) added to the roster with {equipment}."

    except sqlite3.IntegrityError:
        logger.warning(
            f"Recruitment failed: Hunter '{name}' likely already exists (IntegrityError)."
        )
        return f"⚠️ ERROR: A hunter named '{name}' might already exist in the database."
    except Exception as e:
        logger.error(f"Error executing recruit_new_hunter: {e}", exc_info=True)
        return "❌ Internal System Error during recruitment."


@mcp.tool()
async def list_available_hunters(ctx: Context) -> str:
    """Lists all students currently available for missions."""
    logger.info("Tool called: list_available_hunters")
    await ctx.info("Tool called: list_available_hunters")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hunters WHERE status='AVAILABLE'")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            logger.info("Query complete: No hunters available.")
            await ctx.info("Query complete: No hunters available.")
            return "⚠️ NO HUNTERS AVAILABLE."

        logger.info(f"Query complete: Found {len(rows)} available hunters.")
        await ctx.info(f"Query complete: Found {len(rows)} available hunters.")
        roster = "🛡️ AVAILABLE HUNTERS:\n"
        for row in rows:
            roster += f"- {row['name']} ({row['major']}) | Gear: {row['equipment']}\n"
        return roster

    except Exception as e:
        logger.error(f"Error executing list_available_hunters: {e}", exc_info=True)
        return "❌ Internal System Error while fetching roster."


if __name__ == "__main__":
    mcp.run(log_level="INFO")
