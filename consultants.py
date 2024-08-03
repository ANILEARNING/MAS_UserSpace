import streamlit as st
import base64

def create_consultant_box(name, photo_path, role, whatsapp_number):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(photo_path, width=150)
    
    with col2:
        st.subheader(name)
        st.write(role)
        
        whatsapp_url = f"https://wa.me/{whatsapp_number}"
        st.markdown(f"[![Message](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)]({whatsapp_url})")

def main():
    st.title("Consultants")

    consultants = [
        {
            "name": "Anish S",
            "photo": "assets/anish.jpg",
            "role": "Full Stack Data Scientist - Cricket",
            "whatsapp": "8903541468"
        },
        {
            "name": "Ankit Gujare",
            "photo": "assets/ankit.jpg",
            "role": "Cricket Social Media Expert",
            "whatsapp": "9967868733"
        },
        # {
        #     "name": "Mike Johnson",
        #     "photo": "path/to/mike_johnson.jpg",
        #     "role": "Technical Expert",
        #     "whatsapp": "5555555555"
        # },
        # {
        #     "name": "Sarah Brown",
        #     "photo": "path/to/sarah_brown.jpg",
        #     "role": "Project Manager",
        #     "whatsapp": "8903541468"
        # }
    ]

    col1, col2 = st.columns(2)

    for i, consultant in enumerate(consultants):
        with col1 if i % 2 == 0 else col2:
            create_consultant_box(
                consultant["name"],
                consultant["photo"],
                consultant["role"],
                consultant["whatsapp"]
            )
            st.write("---")

# if __name__ == "__main__":
#     main()
