import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from utils.hil_queue import all_items, update_item, replace_draft, remove_item
from agents.email_sender import EmailSenderAgent
from utils.logger import log_send, log_event  # if your logger.py exposes these

st.set_page_config(page_title="Email Assistant - Human Review", page_icon="📩", layout="wide")
st.title("📩 Human-in-the-Loop Review")

def load_queue():
    items = all_items()
    pending = [it for it in items if it.get("status") in ("pending", "approved")]  # show approved until sent
    return pending

items = load_queue()

if not items:
    st.success("No items pending review. 🎉")
    st.stop()

for it in items:
    email = it["email"]
    draft = it["draft"]
    col = st.container()
    with col:
        st.markdown("---")
        st.subheader(f"From: {email['sender']}")
        st.caption(f"Subject: {email['subject']}")
        st.write("**Email Body**")
        st.code(email["body"])

        st.write(f"**LLM Confidence:** {draft.get('confidence', '?')}/10")
        edited = st.text_area("Draft reply", draft.get("reply", ""), key=f"reply_{it['id']}", height=180)

        c1, c2, c3, c4 = st.columns([1,1,1,2])

        if c1.button("✅ Approve", key=f"approve_{it['id']}"):
            replace_draft(it["id"], edited)
            update_item(it["id"], status="approved")
            st.toast("Approved. You can press 'Send now' to dispatch.", icon="✅")

        if c2.button("✏️ Save edit", key=f"save_{it['id']}"):
            replace_draft(it["id"], edited)
            st.toast("Draft updated.", icon="✏️")

        if c3.button("❌ Reject", key=f"reject_{it['id']}"):
            update_item(it["id"], status="rejected")
            st.toast("Rejected. (You can trigger regeneration in your pipeline.)", icon="⚠️")

        if c4.button("📤 Send now", key=f"send_{it['id']}"):
            # send immediately using your MailSlurp inbox
            try:
                sender = EmailSenderAgent()
                sender.send_email(
                    to_email=email["sender"],
                    subject=f"Re: {email['subject']}",
                    body=edited
                )
                update_item(it["id"], status="sent")
                # Optional structured log if you use agents/logger.py with log_send/log_event
                try:
                    log_send(email_id=email.get("id", "unknown"), thread_id=it.get("thread_id", "unknown"),
                             to_email=email["sender"], subject=f"Re: {email['subject']}")
                except Exception:
                    pass
                st.toast("Email sent ✅", icon="📤")
            except Exception as e:
                st.error(f"Failed to send: {e}")
                try:
                    log_event("hil_send_error", {"error": str(e)}, hil_id=it["id"])
                except Exception:
                    pass

st.markdown("---")
st.caption("Tip: Use the 'Rerun' button in the top-right if you don’t see newest items.")
