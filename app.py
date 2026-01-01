import streamlit as st
import google.generativeai as genai

# 1. Cấu hình trang web
st.set_page_config(page_title="Chatbot Team", page_icon="🤖")
st.title("🤖 Trợ lý AI của Team")

# 2. Kết nối với Google Gemini (Lấy API Key từ hệ thống bảo mật)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("Chưa cấu hình API Key. Hãy vào cài đặt của Streamlit để thêm nhé!")
    st.stop()

# Chọn model (dùng bản Flash cho nhanh và miễn phí)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Khởi tạo lịch sử chat nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Hiển thị lịch sử chat cũ lên màn hình
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Xử lý khi người dùng nhập tin nhắn mới
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    # Hiện câu hỏi của người dùng
    with st.chat_message("user"):
        st.markdown(prompt)
    # Lưu vào lịch sử
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Gửi qua Google Gemini để lấy câu trả lời
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Tạo ngữ cảnh từ lịch sử chat (để bot nhớ câu trước)
        chat = model.start_chat(history=[
            {"role": m["role"], "parts": [m["content"]]} 
            for m in st.session_state.messages[:-1] # Lấy lịch sử trừ câu mới nhất
        ])
        
        # Nhận phản hồi (Stream - hiện chữ dần dần cho đẹp)
        response = chat.send_message(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    # Lưu câu trả lời của AI vào lịch sử
    st.session_state.messages.append({"role": "model", "content": full_response})
