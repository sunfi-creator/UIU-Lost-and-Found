import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import os
import csv
from datetime import datetime

CSV_FILE = "lost_and_found.csv"

class LostAndFoundSystem:
    def __init__(self):
        self.ensure_csv()

    @staticmethod
    def ensure_csv():
        """Ensure the CSV file exists with the required headers."""
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Type", "Item Name", "Category", "Location", "Description", "Date", "Finder Contact", "Image"])

    def run(self):
        """Main interface for the Lost and Found system."""
        st.sidebar.title("Lost and Found Management System")

        # Sidebar options for navigation
        user_type = st.sidebar.radio("Login as", ["Student", "Admin"], index=0)

        if user_type == "Student":
            StudentDashboard().login()
        elif user_type == "Admin":
            AdminDashboard().login()

class StudentDashboard:
    def login(self):
        """Student login interface."""
        if "student_logged_in" not in st.session_state:
            st.session_state.student_logged_in = False

        if st.session_state.student_logged_in:
            self.dashboard()
        else:
            # Display UIU campus image and welcome message on the Student login interface
            st.image("uiu_campus.jpg", use_container_width=True)
            st.markdown(
                """
                Welcome to the **UIU Lost and Found**! 
                This platform allows you to report and track lost or found items within our campus.
                """
            )
            st.title("Student Login")
            name = st.text_input("Enter your name")
            student_id = st.text_input("Enter your Student ID")
            if st.button("Login"):
                if name and student_id:
                    st.session_state.student_logged_in = True
                    st.session_state.student_name = name
                    st.session_state.student_id = student_id
                    st.success(f"Welcome, {name}!")
                    self.dashboard()
                else:
                    st.error("Please fill in all fields.")

    def dashboard(self):
        """Student dashboard."""
        st.title(f"Welcome, {st.session_state.student_name}!")
        menu = ["Report Lost Item", "Report Found Item", "View Lost Items", "View Found Items", "Search Items"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Report Lost Item":
            self.report_item("Lost")
        elif choice == "Report Found Item":
            self.report_item("Found")
        elif choice == "View Lost Items":
            self.view_items("Lost")
        elif choice == "View Found Items":
            self.view_items("Found")
        elif choice == "Search Items":
            self.search_items()

        if st.button("Logout"):
            st.session_state.student_logged_in = False
            st.session_state.student_name = None
            st.session_state.student_id = None
            st.success("Logged out successfully.")
            self.login()

    def report_item(self, item_type):
        """Report a lost or found item."""
        st.subheader(f"Report {item_type} Item")
        item_name = st.text_input("Item Name")
        category = st.selectbox("Category", ["Electronics", "Clothing", "Books", "Accessories", "Others"], index=0)
        location = st.text_input("Location")
        description = st.text_area("Description")
        date = st.date_input("Date", datetime.today())
        contact_info = st.text_input("Your Contact Info")
        image = st.file_uploader("Upload Image (optional)", type=["jpg", "png", "jpeg"])

        if st.button("Submit"):
            if not item_name or not category or not location or not description or not contact_info:
                st.error("Please fill in all fields.")
                return

            image_path = None
            if image:
                image_path = f"images/{item_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                os.makedirs("images", exist_ok=True)
                with open(image_path, "wb") as f:
                    f.write(image.getbuffer())

            with open(CSV_FILE, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([item_type, item_name, category, location, description, date, contact_info, image_path])
            st.success(f"{item_type} item reported successfully!")

    @staticmethod
    def view_items(item_type):
        """View lost or found items."""
        st.subheader(f"{item_type} Items")
        if os.path.exists(CSV_FILE):
            data = pd.read_csv(CSV_FILE)
            filtered_data = data[data["Type"] == item_type]

            if not filtered_data.empty:
                for index, row in filtered_data.iterrows():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Item Name:** {row['Item Name']}")
                        st.write(f"**Category:** {row['Category']}")
                        st.write(f"**Location:** {row['Location']}")
                        st.write(f"**Description:** {row['Description']}")
                        st.write(f"**Date:** {row['Date']}")
                        st.write(f"**Contact Info:** {row['Finder Contact']}")
                    with col2:
                        image_path = row.get("Image", None)
                        if pd.notna(image_path) and image_path and os.path.exists(image_path):
                            st.image(image_path, caption="Item Image", use_container_width=True)
                        else:
                            st.info("No image uploaded.")
            else:
                st.info(f"No {item_type} items found.")
        else:
            st.warning("No data available.")

    @staticmethod
    def search_items():
        """Search items by category."""
        st.subheader("Search Items")
        if os.path.exists(CSV_FILE):
            data = pd.read_csv(CSV_FILE)
            category = st.text_input("Enter Category to Search")
            if st.button("Search"):
                filtered_data = data[data["Category"].str.contains(category, case=False, na=False)]
                if not filtered_data.empty:
                    for index, row in filtered_data.iterrows():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Item Name:** {row['Item Name']}")
                            st.write(f"**Category:** {row['Category']}")
                            st.write(f"**Location:** {row['Location']}")
                            st.write(f"**Description:** {row['Description']}")
                            st.write(f"**Date:** {row['Date']}")
                            st.write(f"**Contact Info:** {row['Finder Contact']}")
                        with col2:
                            image_path = row.get("Image", None)
                            if pd.notna(image_path) and image_path and os.path.exists(image_path):
                                st.image(image_path, caption="Item Image", use_container_width=True)
                            else:
                                st.info("No image uploaded.")
                else:
                    st.info("No items found matching the search criteria.")
        else:
            st.warning("No data available.")

class AdminDashboard:
    def login(self):
        """Admin login interface."""
        if "admin_logged_in" not in st.session_state:
            st.session_state.admin_logged_in = False

        if st.session_state.admin_logged_in:
            self.dashboard()
        else:
            st.title("Admin Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if username == "admin" and password == "password":
                    st.session_state.admin_logged_in = True
                    st.success("Logged in successfully!")
                    self.dashboard()
                else:
                    st.error("Invalid credentials.")

    def dashboard(self):
        """Admin dashboard interface."""
        st.title("Admin Dashboard")
        st.markdown("""
        ### Welcome, Admin!
        Use the menu below to manage and analyze Lost and Found items.
        """)

        if os.path.exists(CSV_FILE):
            data = pd.read_csv(CSV_FILE)
            total_items = len(data)
            lost_items = len(data[data["Type"] == "Lost"])
            found_items = len(data[data["Type"] == "Found"])
        else:
            total_items = lost_items = found_items = 0

        st.subheader("Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Items", total_items)
        col2.metric("Lost Items", lost_items)
        col3.metric("Found Items", found_items)

        menu = ["View Lost Items", "View Found Items", "Search Items", "Data Visualization"]
        choice = st.selectbox("Menu", menu)

        if choice == "View Lost Items":
            self.view_items("Lost")
        elif choice == "View Found Items":
            self.view_items("Found")
        elif choice == "Search Items":
            self.search_items()
        elif choice == "Data Visualization":
            self.visualize_data()

        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.success("Logged out successfully.")
            self.login()

    @staticmethod
    def view_items(item_type):
        """View lost or found items."""
        st.subheader(f"{item_type} Items")
        if os.path.exists(CSV_FILE):
            data = pd.read_csv(CSV_FILE)
            filtered_data = data[data["Type"] == item_type]
            if not filtered_data.empty:
                for index, row in filtered_data.iterrows():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Item Name:** {row['Item Name']}")
                        st.write(f"**Category:** {row['Category']}")
                        st.write(f"**Location:** {row['Location']}")
                        st.write(f"**Description:** {row['Description']}")
                        st.write(f"**Date:** {row['Date']}")
                        st.write(f"**Contact Info:** {row['Finder Contact']}")
                    with col2:
                        image_path = row.get("Image", None)
                        if pd.notna(image_path) and image_path and os.path.exists(image_path):
                            st.image(image_path, caption="Item Image", use_container_width=True)
                        else:
                            st.info("No image uploaded.")
            else:
                st.info(f"No {item_type} items found.")
        else:
            st.warning("No data available.")

    @staticmethod
    def search_items():
        """Search items by category."""
        st.subheader("Search Items")
        if os.path.exists(CSV_FILE):
            data = pd.read_csv(CSV_FILE)
            category = st.text_input("Enter Category to Search")
            if st.button("Search"):
                filtered_data = data[data["Category"].str.contains(category, case=False, na=False)]
                if not filtered_data.empty:
                    for index, row in filtered_data.iterrows():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Item Name:** {row['Item Name']}")
                            st.write(f"**Category:** {row['Category']}")
                            st.write(f"**Location:** {row['Location']}")
                            st.write(f"**Description:** {row['Description']}")
                            st.write(f"**Date:** {row['Date']}")
                            st.write(f"**Contact Info:** {row['Finder Contact']}")
                        with col2:
                            image_path = row.get("Image", None)
                            if pd.notna(image_path) and image_path and os.path.exists(image_path):
                                st.image(image_path, caption="Item Image", use_container_width=True)
                            else:
                                st.info("No image uploaded.")
                else:
                    st.info("No items found matching the search criteria.")
        else:
            st.warning("No data available.")

    @staticmethod
    def visualize_data():
        """Visualize data with various charts."""
        st.subheader("Data Visualization")
        if os.path.exists(CSV_FILE):
            data = pd.read_csv(CSV_FILE)

            if data.empty:
                st.warning("No data available for visualization.")
                return

            chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Pie Chart", "Line Graph", "Scatter Plot", "Location Distribution"])

            if chart_type == "Bar Chart":
                chart_data = data["Category"].value_counts()
                fig = plt.figure(figsize=(10, 5))
                sns.barplot(x=chart_data.index, y=chart_data.values, palette="viridis")
                plt.title("Item Categories")
                plt.xlabel("Category")
                plt.ylabel("Count")
                st.pyplot(fig)

            elif chart_type == "Pie Chart":
                chart_data = data["Type"].value_counts()
                fig = px.pie(values=chart_data.values, names=chart_data.index, title="Lost vs Found Items")
                st.plotly_chart(fig)

            elif chart_type == "Line Graph":
                data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
                data.dropna(subset=["Date"], inplace=True)
                chart_data = data.groupby("Date").size()
                fig = px.line(x=chart_data.index, y=chart_data.values, labels={"x": "Date", "y": "Count"}, title="Items Over Time")
                st.plotly_chart(fig)

            elif chart_type == "Scatter Plot":
                data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
                scatter_fig = px.scatter(data, x="Date", y="Category", color="Type", title="Scatter Plot of Items")
                st.plotly_chart(scatter_fig)

            elif chart_type == "Location Distribution":
                location_data = data[data["Type"] == "Lost"]["Location"].value_counts()
                fig = plt.figure(figsize=(10, 5))
                sns.barplot(x=location_data.index, y=location_data.values, palette="viridis")
                plt.title("Locations with Most Lost Items")
                plt.xlabel("Location")
                plt.ylabel("Count")
                st.pyplot(fig)

        else:
            st.warning("No data available.")

if __name__ == "__main__":
    system = LostAndFoundSystem()
    system.run()