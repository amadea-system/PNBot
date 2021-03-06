import aiosqlite
import logging
import time
import functools

from datetime import datetime
from typing import Optional, List, Dict

log = logging.getLogger("PNBot.db")


def db_deco(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            response = await func(*args, **kwargs)
            end_time = time.perf_counter()
            if len(args) > 1:
                log.info("DB Query {} from {} in {:.3f} ms.".format(func.__name__, args[1], (end_time - start_time) * 1000))
            else:
                log.info("DB Query {} in {:.3f} ms.".format(func.__name__, (end_time - start_time) * 1000))
            return response
        except Exception:
        # except asyncpg.exceptions.PostgresError:
            log.exception("Error attempting database query: {} for server: {}".format(func.__name__, args[1]))
    return wrapper


# ---------- Interview Methods ---------- #

# --- Inserts --- #
# @db_deco
# async def add_new_interview(db: str, sid: int, member_id: int, username: str, channel_id: int):
#     async with aiosqlite.connect(db) as conn:
#         await conn.execute(
#             "INSERT INTO interviews(guild_id, member_id, user_name, channel_id, join_ts) VALUES(?, ?, ?, ?, ?)",
#             (sid, member_id, username, channel_id, datetime.utcnow()))
#         await conn.commit()
#

@db_deco
async def add_new_interview(db: str, sid: int, member_id: int, username: str, channel_id: int,
                                  question_number: int = 0, interview_finished: bool = False, paused: bool = False,
                                  interview_type: str = 'unknown', read_rules: bool = False, join_ts: datetime = datetime.utcnow()):
    async with aiosqlite.connect(db) as conn:
        # Convert ts to str
        ts = join_ts.isoformat()
        await conn.execute(
            "INSERT INTO interviews(guild_id, member_id, user_name, channel_id, question_number, interview_finished, paused, interview_type, read_rules, join_ts) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (sid, member_id, username, channel_id, question_number, interview_finished, paused, interview_type, read_rules, ts))
        await conn.commit()


# --- Updates --- #
@db_deco
async def update_interview_all_mutable(db: str, cid: int, mid: int, question_number: int, interview_finished: bool, paused: bool, interview_type: str, read_rules: bool):
    async with aiosqlite.connect(db) as conn:
        await conn.execute(
            "UPDATE interviews SET question_number = ?, interview_finished = ?, paused = ?, interview_type = ?, read_rules = ? WHERE channel_id = ? AND member_id = ?",
            (question_number, interview_finished, paused, interview_type, read_rules, cid, mid))
        await conn.commit()


@db_deco
async def update_interview_question_number(db: str, cid: int, mid: int, question_number: int):
    async with aiosqlite.connect(db) as conn:
        await conn.execute(
            "UPDATE interviews SET question_number = ? WHERE channel_id = ? AND member_id = ?",
            (question_number, cid, mid))
        await conn.commit()


@db_deco
async def update_interview_finished(db: str, cid: int, mid: int, interview_finished: bool):
    async with aiosqlite.connect(db) as conn:
        await conn.execute(
            "UPDATE interviews SET interview_finished = ? WHERE channel_id = ? AND member_id = ?",
            (interview_finished, cid, mid))
        await conn.commit()


@db_deco
async def update_interview_paused(db: str, cid: int, mid: int, paused: bool):
    async with aiosqlite.connect(db) as conn:
        await conn.execute(
            "UPDATE interviews SET paused = ? WHERE channel_id = ? AND member_id = ?",
            (paused, cid, mid))
        await conn.commit()


@db_deco
async def update_interview_type(db: str, cid: int, mid: int, interview_type: str):
    async with aiosqlite.connect(db) as conn:
        await conn.execute(
            "UPDATE interviews SET interview_type = ? WHERE channel_id = ? AND member_id = ?",
            (interview_type, cid, mid))
        await conn.commit()


@db_deco
async def update_interview_read_rules(db: str, cid: int, mid: int, read_rules: bool):
    async with aiosqlite.connect(db) as conn:
        await conn.execute(
            "UPDATE interviews SET read_rules = ? WHERE channel_id = ? AND member_id = ?",
            (read_rules, cid, mid))
        await conn.commit()


# --- Selects --- #
interview_row_map = ('guild_id', 'member_id', 'user_name', 'channel_id', 'question_number', 'interview_finished',
                     'paused', 'interview_type', 'read_rules', 'join_ts')


def row_to_interview_dict(row: aiosqlite.Row) -> Dict:
    interview_dict = {
        interview_row_map[0]: row[0],   # Guild ID
        interview_row_map[1]: row[1],   # Member_id
        interview_row_map[2]: row[2],   # user_name
        interview_row_map[3]: row[3],   # channel_id
        interview_row_map[4]: row[4],   # quest_num
        interview_row_map[5]: bool(row[5]),   # int_fin
        interview_row_map[6]: bool(row[6]),   # Paused
        interview_row_map[7]: row[7],   # interview_type
        interview_row_map[8]: bool(row[8]),   # read_rules
        interview_row_map[9]: datetime.fromisoformat(row[9])  # join_ts
    }
    return interview_dict




# @db_deco
# async def get_interview_by_member(db: str, member_id: int):
#     async with aiosqlite.connect(db) as conn:
#         cursor = await conn.execute(" SELECT * from interviews WHERE member_id = ?", (member_id,))
#         row = await cursor.fetchone()
#         # interview_dict = dict(zip(interview_row_map, row))
#
#         return row_to_interview_dict(row)
#
#
# @db_deco
# async def get_all_interview_for_guild(db: str, sid: int):
#     async with aiosqlite.connect(db) as conn:
#         cursor = await conn.execute(" SELECT * from interviews WHERE guild_id = ?", (sid,))
#         raw_rows = await cursor.fetchall()
#         # rows = [dict(zip(interview_row_map, row)) for row in raw_rows]
#         rows = []
#         for row in raw_rows:
#             rows.append(row_to_interview_dict(row))
#         return rows


@db_deco
async def get_all_interviews(db: str):
    async with aiosqlite.connect(db) as conn:
        cursor = await conn.execute(" SELECT * from interviews")
        raw_rows = await cursor.fetchall()
        # rows = [dict(zip(interview_row_map, row)) for row in raw_rows]
        rows = []
        for row in raw_rows:
            rows.append(row_to_interview_dict(row))
        return rows


# --- Deletes --- #
@db_deco
async def delete_interview(db: str, cid: int, mid: int):
    async with aiosqlite.connect(db) as conn:
        await conn.execute(
            "DELETE FROM interviews WHERE channel_id = ? AND member_id = ?",
            (cid, mid))
        await conn.commit()


# --- Guild Settings --- #

@db_deco
async def do_guild_settings_exist(db: str, sid: int) -> bool:
    async with aiosqlite.connect(db) as conn:
        cursor = await conn.execute(
            """
            SELECT COUNT(*) FROM guild_settings WHERE guild_id = ?
            """, (sid,)
        )
        row = await cursor.fetchone()
        if row is not None and row[0] > 0:
            return True
        else:
            return False

@db_deco
async def upsert_raid_level(db: str, sid: int, raid_level: int):
    async with aiosqlite.connect(db) as conn:
        if await do_guild_settings_exist(db, sid):
            await conn.execute("UPDATE guild_settings SET raid_level = ? WHERE guild_id = ?", (raid_level, sid))
        else:
            await conn.execute("INSERT INTO guild_settings(guild_id, raid_level) VALUES(?, ?)", (sid, raid_level)
            # ON CONFLICT(guild_id)
            # DO UPDATE SET raid_level = EXCLUDED.raid_level
            )
        await conn.commit()


@db_deco
async def get_raid_level(db: str, sid: int) -> int:
    async with aiosqlite.connect(db) as conn:
        cursor = await conn.execute(" SELECT * from guild_settings WHERE guild_id = ?", (sid,))
        row = await cursor.fetchone()
        # interview_dict = dict(zip(interview_row_map, row))

        if row is not None:
            return row[1]
        else:
            return 0

# ---------- Table Creation ---------- #
@db_deco
async def create_tables(db: str):
    async with aiosqlite.connect(db) as conn:
        # TODO: Move interview_type over to an int and use an enum?
        await conn.execute('''
                               CREATE TABLE if not exists interviews (
                               guild_id             BIGINT NOT NULL,
                               member_id            BIGINT NOT NULL,
                               user_name            TEXT NOT NULL,
                               channel_id           BIGINT NOT NULL,
                               question_number      INT DEFAULT 0,
                               interview_finished   BOOLEAN default FALSE,
                               paused               BOOLEAN default FALSE,
                               interview_type       TEXT default 'unknown',   
                               read_rules           BOOLEAN default FALSE,
                               join_ts              TEXT,
                               PRIMARY KEY          (member_id, channel_id)
                              );
                        ''')

        await conn.execute('''
                               CREATE TABLE if not exists guild_settings (
                               guild_id                 BIGINT NOT NULL,
                               raid_level               INT DEFAULT 0,
                               PRIMARY KEY              (guild_id)
                              );
                        ''')

        # await conn.execute('''
        #                        CREATE TABLE if not exists rule_confirmations (
        #                        member_id        BIGINT NOT NULL,
        #                        guild_id         BIGINT NOT NULL,
        #                        question_number  INT,
        #                        paused           BOOLEAN,
        #                        interview_type   TEXT,
        #                        user_name        TEXT NOT NULL,
        #                        content          TEXT DEFAULT NULL
        #                    );
        #                     ''')
