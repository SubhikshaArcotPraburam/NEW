import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image
import time
@st.cache_resource
def get_gsheet():
    credentials_dict = dict(st.secrets["gspread"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
    gc = gspread.authorize(credentials)
    return gc.open_by_key(credentials_dict["gsheet_key"])

@st.cache_data
def load_design():
    return pd.read_csv("optimized_design.csv")

def load_pre_rendered_image(D2D_value):
    path = f"door_images/door_d2d_{D2D_value}.png"
    return Image.open(path)

# Session State Initialization
if 'page' not in st.session_state:
    st.session_state.page = 'start'
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'demographic_data' not in st.session_state:
    st.session_state.demographic_data = {}

ticket_price = 3.8
trip_duration = 60
design = load_design()
counter = st.session_state.get("counter", 0)
trip_duration = 60

# --- Get participant counter from Google Sheet ---
if 'counter' not in st.session_state:
    sheet_meta = get_gsheet().worksheet("Meta")
    counter_cell = sheet_meta.acell("A2").value
    if counter_cell is None or counter_cell.strip() == "":
        st.error("Error: Meta sheet cell A2 is empty. Please initialize it with a number (e.g., 0).")
        st.stop()
    st.session_state.counter = int(counter_cell)

counter = st.session_state.counter
group_id = counter % 4

travel_contexts = {
    0: "With friends and luggage",
    1: "Business traveler, urgent schedule",
    2: "Alone with a backpack",
    3: "In a group with a bike"
}

travel_context = travel_contexts[group_id]

st.session_state.ticket_price = ticket_price
st.session_state.trip_duration = trip_duration
st.session_state.travel_context = travel_context

# --- HELPER FUNCTION ---
def load_pre_rendered_image(D2D_value):
    path = f"door_images/door_d2d_{D2D_value}.png"
    return Image.open(path)

# --- START PAGE ---
if st.session_state.page == 'start':
    st.title("Welcome to the Train Door Choice Experiment")

    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()

    st.markdown("""
    Dear Participant,

    Thank you for your interest in this study!

    In this survey, we explore how passengers choose between different subway doors when boarding a train.

    ---

    Please read the following information carefully before starting the survey.

    **Set-up:**

    Imagine you are standing on a subway platform, about to decide where to wait for an arriving train. 
    You haven’t positioned yourself yet and must now choose a spot on the platform.

  

    ---

    **How it works?**

    - You'll see 12 decision tasks, each showing 2 subway doors (A, B).
    - For each task, compare the doors and select the one you'd choose to board from.
    - All doors are part of the same train, arriving now.
    - Make your decision as if you're on the platform in real life.
    """)

    st.markdown("### Attributes You'll See")


    attribute_list = [
    ("👣  Walking distance to the door (D2D)", "How far you’d walk on the platform to reach it (in meters)."),
    ("🛤  Distance to station exit (D2E)", "How far you’ll walk after arriving at your destination (in meters)."),
    ("🚧  Obstacle (O)", "Whether there is a physical obstacle between you and the door."),
    ("🧍  People waiting (CD)", "The number of people already lined up outside the door."),
    ("🚶‍♀️  Crowding on Platform (CP)", "How crowded the platform is near the door (people per square meter)."),
    ("📺  Crowdedness on screen (CTD)", "Crowdedness info on display screen. Options: Green = low crowd, Yellow = medium crowd, Red = high crowd."),
    ("🟦  LED stripe indicator (CTL)", "Crowdedness info via LED ground stripes. Options: Green = low crowd, Yellow = medium crowd, Red = high crowd."),
    ("💸  Discount offered (D)", "The fare discount percentage you’d receive for using this door."),
    ("⏱  Train arrives in (T2DR)", "Number of minutes until this train arrives."),
    ("🕓  Next train in (T2DS)", "If you skip this train, how long until the next one (in minutes)."),
    ("🧭  Trip shift indicator (TS)", "current train, a later train (e.g., delay or alternate option)."),
    ("🔄  Transfer History (TR)", "no transfer, transferred + changed doors, transferred + same door")
]


    for attr, explanation in attribute_list:
        col1, col2 = st.columns([2.5, 4])
        with col1:
            st.markdown(f"**{attr}**")
        with col2:
            st.markdown(explanation)

    st.markdown(f"""
    ---

    **Other Information:**

    - Ticket price: Your regular ticket costs **{ticket_price} Euros**. This remains constant.
    - Trip duration: Your trip takes **{trip_duration} minutes**.
    - You are traveling in this experiment: **{travel_context}**

    Respond naturally — there's no "right" answer.

    Your choices help us understand what matters to passengers.

    ---

    **Demographic Information:**

    At the end, we’ll ask some optional background questions (e.g., age, gender, travel frequency).

    **Data Protection and Confidentiality:**
    - Participation is voluntary, you can withdraw anytime.
    - Data is anonymous and for academic research only.
    - We comply with GDPR/DSGVO.

    Contact: 
    subhiksha.praburam@rwth-aachen.de

    sangita.conjeevaram-viswanathan@rwth-aachen.de

    aaryan.tarambale@rwth-aachen.de

    ---

    By continuing, you confirm that you have read and understood the information and agree to participate.
    """)

    st.markdown("### Quick Check Before Starting")
    st.markdown("Please answer these short questions to proceed:")

    with st.form("comprehension_form"):
        price_options = [
            f"€{ticket_price - 2:.2f}",
            f"€{ticket_price - 1:.2f}",
            f"€{ticket_price:.2f}",
            f"€{ticket_price + 1:.2f}"
        ]
        answer_price = st.radio("1. What is the regular ticket price for your trip in this experiment?",
                                 options=price_options, key="comprehension_price")

        duration_options = [
            f"10 minutes",
            f"20 minutes",
            f"30 minutes",
            f"{trip_duration} minutes"
        ]
        answer_duration = st.radio("2. How long is your trip from origin to destination?",
                                    options=duration_options, key="comprehension_duration")

        travel_options = list(travel_contexts.values())
        answer_alone = st.radio("3. How are you traveling in this experiment?",
                                 options=travel_options, key="comprehension_alone")

        confirm_clicked = st.form_submit_button("Confirm Answers")

    if confirm_clicked:
        is_correct_alone = answer_alone == st.session_state.travel_context

        if is_correct_alone:
            st.success("Correct – you may now proceed to the survey.")
            st.session_state.allow_start = True
        else:
            st.error("One or more answers are incorrect. Please read the instructions above again carefully.")
            st.session_state.allow_start = False

    # --- Conditional start button ---
    if st.session_state.get("allow_start", False) and st.button("Start Survey"):
        st.session_state.page = 'survey'
        st.session_state.current_idx = 0  # reset index
        st.rerun()


#SURVEY PAGE

elif st.session_state.page == 'survey':
    st.title("Train Door Choice Survey")
    
    st.write(f"""
    Imagine you are traveling {st.session_state.travel_context.lower()}.

    Remember: The regular ticket price for this trip is **{ticket_price} Euros**.  
    Each door option may offer a discount that will reduce this price.

    Remember: The total travel time for your trip is **{trip_duration} minutes**. 
    """)

    questions = design.copy().reset_index(drop=True)
    total_questions = len(questions)
    idx = st.session_state.current_idx

    if f"temp_choice_{idx}" not in st.session_state:
        st.session_state[f"temp_choice_{idx}"] = st.session_state.responses.get(idx, "Door A")

    question = questions.iloc[idx]
    st.markdown(f"### Question {idx+1} of {total_questions}: Which door do you choose?")

    image_A = load_pre_rendered_image(question['A_D2D'])
    image_B = load_pre_rendered_image(question['B_D2D'])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Door A")
        st.image(image_A, caption="Option A", use_container_width=True)
        st.markdown(f"- **Walking distance (D2D)**: {question['A_D2D']} m")
        st.markdown(f"- **Distance to exit (D2E)**: {question['A_D2E']} m")
        st.markdown(f"- **Obstacle (O)**: {question['A_O']}")
        st.markdown(f"- **People waiting (CD)**: {question['A_CD']} people")
        st.markdown(f"- **Crowding on platform (CP)**: {question['A_CP']} people/m²")
        st.markdown(f"- **Discount offered (D)**: {question['A_D']}% → you pay €{ticket_price * (1 - question['A_D'] / 100):.2f}")
        st.markdown(f"- **Train arrives in (T2DR)**: {question['A_T2DR']} min")
        if question['A_TS'] != question['A_T2DS']:
            st.markdown(f"- **Next train in (T2DS)**: {question['A_T2DS']} min")
            st.markdown(f"- **Trip shift (TS)**: {question['A_TS']}")
        if question['A_TR_doorchange'] == 1:
            st.markdown("- **Transfer history (TR)**: There was a door change in the previous trip.")
        elif question['A_TR_nochange'] == 1:
            st.markdown("- **Transfer history (TR)**: There was no door change in the previous trip.")


    with col2:
        st.subheader("Door B")
        st.image(image_B, caption="Option B", use_container_width=True)
        st.markdown(f"- **Walking distance (D2D)**: {question['B_D2D']} m")
        st.markdown(f"- **Distance to exit (D2E)**: {question['B_D2E']} m")
        st.markdown(f"- **Obstacle (O)**: {question['B_O']}")
        st.markdown(f"- **People waiting (CD)**: {question['B_CD']} people")
        st.markdown(f"- **Crowding on platform (CP)**: {question['B_CP']} people/m²")
        st.markdown(f"- **Discount offered (D)**: {question['B_D']}% → you pay €{ticket_price * (1 - question['B_D'] / 100):.2f}")
        st.markdown(f"- **Train arrives in (T2DR)**: {question['B_T2DR']} min")
        if question['B_TS'] != question['B_T2DS']:
            st.markdown(f"- **Next train in (T2DS)**: {question['B_T2DS']} min")
            st.markdown(f"- **Trip shift (TS)**: {question['B_TS']}")
        if question['B_TR_doorchange'] == 1:
            st.markdown("- **Transfer history (TR)**: There was a door change in the previous trip.")
        elif question['B_TR_nochange'] == 1:
            st.markdown("- **Transfer history (TR)**: There was no door change in the previous trip.")




    with st.form(key=f"form_{idx}"):
        st.session_state[f"temp_choice_{idx}"] = st.radio(
            "Which option do you choose?",
            ("Door A", "Door B", "None of both"),
            index=("Door A", "Door B", "None of both").index(st.session_state[f"temp_choice_{idx}"])
        )

        col_back, col_next = st.columns([1, 5])
        with col_back:
            back_clicked = st.form_submit_button("Back")
        with col_next:
            next_clicked = st.form_submit_button("Next" if idx < total_questions - 1 else "Submit Survey")

        if back_clicked and idx > 0:
            st.session_state.current_idx -= 1
            st.rerun()

        if next_clicked:
            st.session_state.responses[idx] = st.session_state[f"temp_choice_{idx}"]
            if idx < total_questions - 1:
                st.session_state.current_idx += 1
                st.rerun()
            else:
                # Save responses
                df_responses = pd.DataFrame([
                    {
                        'participant_number': counter,
                        'ticket_price': ticket_price,
                        'trip_duration': trip_duration,
                        'choice_set': i + 1,
                        'choice': st.session_state.responses[i],
                        **design.iloc[i].to_dict()
                    }
                    for i in range(total_questions)
                ])
                get_gsheet().worksheet("Responses").append_rows(df_responses.values.tolist(), value_input_option="USER_ENTERED")
                st.session_state.page = 'demographics'
                st.rerun()
elif st.session_state.page == 'demographics':
    st.title("A Few More Questions")
    st.write("""

    To better understand the survey results, we would like to ask you a few additional questions.  
    Your answers are completely voluntary, anonymous, and will only be used for academic research purposes.
    """)

    with st.form("demographics_form"):
        age = st.selectbox(
            "What is your age group?",
            ["Prefer not to say", "18–29", "30–39", "40–49", "50–59", "60–69", "70+"]
        )


        gender = st.selectbox(
            "What is your gender?",
            ["Prefer not to say", "Female", "Male", "Diverse"]
        )

        travel_freq = st.selectbox(
            "How often have you approximately traveled by train in the last 12 months?",
            ["Prefer not to say", "None", "Daily", "Weekly", "Monthly", "Yearly"]
        )

        travel_freq_1 = st.selectbox(
            "How often have you approximately traveled by ***subway*** in the last 12 months?",
            ["Prefer not to say", "None", "Daily", "Weekly", "Monthly", "Yearly"]
        )

        mobility = st.select_slider(
            "How would you assess your mobility?",
            options=[
                "Prefer not to say",
                "0 - No problems",
                "1 - Minor limitations",
                "2 - Moderate limitations",
                "3 - Severe limitations",
                "4 - Unstable / Handicapped"
            ]
        )
        comments = st.text_area(
            "Do you have any comments, suggestions, or feedback about the survey experience?",
            placeholder="(Optional) You can write here..."
        )

 # how was your survey experince(comment)
        # Make sure this is at the same level as the other inputs
        submitted = st.form_submit_button("Submit Demographic Data")

    if submitted and not st.session_state.get("submitted_demo", False):
    # Save demographic data
        end_time = time.time()
        duration_seconds = int(end_time - st.session_state.start_time)
        duration_minutes = round(duration_seconds / 60, 2)
        start_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.session_state.start_time))
        end_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))

        demographic_response = pd.DataFrame([{
            'participant_number': counter,
            'age': age,
            'gender': gender,
            'travel_frequency': travel_freq,
            'ubahn_frequency': travel_freq_1,
            'mobility': mobility,
            'comment': comments,
            'survey_duration_minutes': duration_minutes,
            'start_timestamp': start_timestamp,
            'end_timestamp': end_timestamp
        }])
   
        sheet_demo = get_gsheet().worksheet("Demographics")
        sheet_demo.append_rows(demographic_response.values.tolist(), value_input_option="USER_ENTERED")
    
        sheet_meta = get_gsheet().worksheet("Meta")
        sheet_meta.update("A2", [[str(counter + 1)]])

        
        st.session_state.submitted_demo = True  # ✅ prevent further submissions
    
        st.session_state.page = 'end'
        st.rerun()

elif st.session_state.page == 'end':
    st.title("Thank You for Your Participation!")

    if 'start_time' in st.session_state:
        total_time = time.time() - st.session_state.start_time
        st.markdown(f"🕓 You completed the survey in **{round(total_time / 60, 2)} minutes**.")


    st.markdown("""
    Your responses have been recorded successfully.

    If you have any questions or would like to know more about this research, feel free to contact:

    Subhiksha Arcot Praburam :  subhiksha.praburam@rwth-aachen.de

    Sangita Conjeevaram Viswanathan : sangita.conjeevaram-viswanathan@rwth-aachen.de

    Aaryan Tarambale: aaryan.tarambale@rwth-aachen.de

    RWTH Aachen University  
    

    ---

    You may now close this tab or window.

    """)
