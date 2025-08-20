# hil_ui/app.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from utils.hil_queue import all_items, update_item, replace_draft
from agents.email_sender import EmailSenderAgent
from utils.logger import log_send

# ---------------------------
# Streamlit Page Config
# ---------------------------
st.set_page_config(page_title="Email Assistant – Human Review", page_icon="📩", layout="wide")
st.title("📩 Human-in-the-Loop Review")

# ---------------------------
# Cached Email Sender
# ---------------------------
@st.cache_resource
def get_sender():
    return EmailSenderAgent()

sender = get_sender()

# ---------------------------
# Load Queue
# ---------------------------
status_filter = st.multiselect(
    "Filter by status",
    ["pending", "approved", "rejected", "sent"],
    default=["pending", "approved"],
)

items = [it for it in all_items() if it.get("status") in status_filter]

if not items:
    st.success("No items matching filter 🎉")
    st.stop()

# ---------------------------
# Render Items
# ---------------------------
for it in items:
    email = it.get("email", {})
    draft = it.get("draft", {})

    st.markdown("---")
    st.subheader(f"From: {email.get('sender','?')}")
    st.caption(f"Subject: {email.get('subject','(no subject)')}")

    with st.expander("📨 Email Body", expanded=True):
        st.code(email.get("body", "(empty)"))

    st.write("**LLM Confidence:**")
    st.progress(min(max(draft.get("confidence", 0) / 10.0, 0), 1.0))

    edited = st.text_area(
        "Draft reply",
        draft.get("reply", ""),
        key=f"reply_{it['id']}",
        height=180
    )

    c1, c2, c3, c4 = st.columns([1,1,1,2])

    if c1.button("✅ Approve", key=f"approve_{it['id']}"):
        replace_draft(it["id"], edited)
        update_item(it["id"], status="approved")
        st.toast("Approved. You can press 'Send now'.", icon="✅")

    if c2.button("✏️ Save edit", key=f"save_{it['id']}"):
        replace_draft(it["id"], edited)
        st.toast("Draft updated.", icon="✏️")

    if c3.button("❌ Reject", key=f"reject_{it['id']}"):
        update_item(it["id"], status="rejected")
        st.toast("Rejected. (Regenerate in pipeline if needed.)", icon="⚠️")

    if c4.button("📤 Send now", key=f"send_{it['id']}"):
        try:
            sender.send_email(
                to_email=email.get("sender", ""),
                subject=f"Re: {email.get('subject','(no subject)')}",
                body=edited,
            )
            update_item(it["id"], status="sent")
            log_send(
                email_id=email.get("id", "?"),
                thread_id=it.get("thread_id", "?"),
                to_email=email.get("sender", ""),
                subject=f"Re: {email.get('subject','(no subject)')}"
            )
            st.toast("Email sent ✅", icon="📤")
        except Exception as e:
            st.error(f"Failed to send: {e}")

st.markdown("---")
st.caption("Tip: click the 'Rerun' button in the top-right if you don’t see new items.")
