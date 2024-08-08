import streamlit as st
import base64

def create_consultant_box(name, photo_path, role,bio, whatsapp_number):
    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(photo_path, width=150)
        
        with col2:
            st.subheader(name)
            st.write(role)
            st.write(bio)
            
            whatsapp_url = f"https://wa.me/{whatsapp_number}"
            st.markdown(f"[![Message](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)]({whatsapp_url})")

def main():
    st.title("Experts")
    
    # Custom CSS for spacing
    st.markdown("""
    <style> 
    .consultant-box {
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    consultants = [
        {
            "name": "Anish S",
            "photo": "assets/anish.jpg",
            "role": "Full Stack Data Scientist - Cricket",
            "whatsapp": "919384972461",
            "bio":"Creator of innovative Cricket solutions through data and technology; And one of my work in your hand(MASUserSpace), Explore how my expertise can transform your game."
        },
        {
            "name": "Ankit Gujare",
            "photo": "assets/ankit.jpg",
            "role": "Cricket Social Media Expert",
            "whatsapp": "919967868733",
            "bio":"I can help you grow your Cricket Page/Channel"
        },
        {
            "name": "Radhika patle",
            "photo": "assets/radhika.jpg",
            "role": "Injury Prevention and Rehabilitation",
            "whatsapp": "919752622331",
            "bio": ""
        },
        {
            "name": "Aniketh Kotamraju",
            "photo": "assets/aniketh.jpg",
            "role": "Content Researcher",
            "whatsapp": "917989072868",
            "bio":""
        }
        
        # Add more consultants here if needed
    ]

    for consultant in consultants:
        with st.container():
            st.markdown('<div class="consultant-box">', unsafe_allow_html=True)
            create_consultant_box(
                consultant["name"],
                consultant["photo"],
                consultant["role"],
                consultant["bio"],
                consultant["whatsapp"]
            )
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
