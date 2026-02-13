#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import datetime
from zoneinfo import ZoneInfo
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ─── 設定 ─────────────────────────────────
SLACK_TOKEN         = os.environ["SLACK_BOT_TOKEN"]

REPORT_CHANNEL_ID   = "CHANNEL_ID"  # Put channnel ID　レポートを読み取るチャンネルのID

GROUP_CHANNELS = {
    "Group A": "Group A Channel ID",
    "Group B": "Group B Channel ID",
    "Group C": "Group C Channel ID",  

} 
# Channel ID mapping for each group to be notified
# リマインドを行うチャンネルのID


client = WebClient(token=SLACK_TOKEN)



def list_reporters():
    """
    return: set of user IDs who have reported
    at least 150 characters and an image since the first of the month

    """

    # timezone
    tokyo = ZoneInfo("Asia/Tokyo")
    start_jst = datetime.datetime.now(tokyo).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    
    # Convert to timestamp
    oldest_ts = start_jst.timestamp()
    cursor = None
    reporters = set()

    while True:
        resp = client.conversations_history(
            channel=REPORT_CHANNEL_ID,
            oldest=oldest_ts,
            limit=200,
            cursor=cursor
        )
        for msg in resp["messages"]:
            user = msg.get("user")
            text = msg.get("text", "")
            files = msg.get("files", [])

            # Check if there is an image in files
            has_image = any(
                f.get("mimetype", "").startswith("image/")
                for f in files
            )

            if user and has_image and len(text) >= 150:
                reporters.add(user)

        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

        time.sleep(1)  # Rate limit handling

    return reporters

def list_group_members(channel_id):
    """
    return: set of user IDs in the specified channel
    """
    members = set()
    cursor = None
    while True:
        resp = client.conversations_members(
            channel=channel_id,
            limit=200,
            cursor=cursor
        )
        members.update(resp["members"])
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
        time.sleep(1)
    return members



def notify_numeric_non_reporters(group_name, channel_id):
    """
    send reminder mentions to numeric-starting members who have not reported this month
    """
    # Start notification
    client.chat_postMessage(
        channel=channel_id,
        text=f"🛠 {group_name} s tarting notification process..."
    )

    now_jst = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
    timestamp = now_jst.strftime("%Y-%m-%d %H:%M") 

    full_reporters = list_reporters()
    print(f"DEBUG: full reporters = {full_reporters}")

    members = list_group_members(channel_id)
    print(f"DEBUG[{group_name}] channel members = {members}")

    ## Extract numeric-starting members
    numeric_members_list = []
    for uid in members:
        try:
            user = client.users_info(user=uid)["user"]
            handle       = user.get("name", "")
            display_name = user.get("profile", {}).get("display_name", "")

            print(f"DEBUG: {uid} → handle='{handle}', display_name='{display_name}'")
            if (handle  and handle[0].isdigit()) or \
               (display_name and display_name[0].isdigit()):
                numeric_members_list.append(uid)
        except SlackApiError as e:
            print(f"⚠️ users_info error for {uid}: {e.response['error']}")
    numeric_members = set(numeric_members_list) 
    
    print(f"DEBUG[{group_name}] numeric_members = {numeric_members}")

    numeric_non_reporters = numeric_members - full_reporters
    print(f"DEBUG[{group_name}] numeric_non_reporters = {numeric_non_reporters}")
    
    if not numeric_non_reporters:
        client.chat_postMessage(
            channel=channel_id,
            text=f"✅ {group_name}：every numeric-starting member has reported!（time: {timestamp}）"
        )
        return
        
        
    mentions = " ".join(f"<@{uid}>" for uid in sorted(numeric_non_reporters))
    text = (
    f"🔔【{group_name}】（time: {timestamp}）"
    f"{mentions} "
    "you need to submit report !!"
    )
    
    client.chat_postMessage(channel=channel_id, text=text)
    print(f"▶️ [{group_name}] remind: {numeric_non_reporters}")
        
if __name__ == "__main__":
    # Start notifications for each group
    for group_name, channel_id in GROUP_CHANNELS.items():
        notify_numeric_non_reporters(group_name, channel_id)
