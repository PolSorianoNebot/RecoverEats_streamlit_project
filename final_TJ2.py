import requests
import json
import requests
import pandas as pd
import streamlit as st
import numpy as np
import random 
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



col1, col2 = st.columns([1, 2])
with col1:
    st.logo("https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/98/e6/3e/98e63ec0-9b3b-6f24-4e5e-091656f4dcd6/AppIcon-0-0-1x_U007emarketing-0-8-0-sRGB-85-220.png/512x512bb.jpg",  size="large", link=None, icon_image=None)
    st.image("https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/98/e6/3e/98e63ec0-9b3b-6f24-4e5e-091656f4dcd6/AppIcon-0-0-1x_U007emarketing-0-8-0-sRGB-85-220.png/512x512bb.jpg", width=100)
with col2:
    st.title("Whoop & Diet APP")
  

url = 'https://api.prod.whoop.com/oauth/oauth2/auth?client_id=3e74d17a-9a9e-4846-bc25-48a5772a2e08&redirect_uri=https://oauth.pstmn.io/v1/callback&response_type=code&scope=read:recovery read:cycles read:profile read:body_measurement read:workout read:sleep&state=12345678'

col1, col2, col3 = st.columns([2, 2, 1])

with col2:
    st.page_link(url, label="Whoop sign in", icon="🔵")

st.markdown("###  Follow the link above to get your Whoop sign in code")

with st.expander("Further Sign-In explanation:"):
    st.write('''
        1. Follow the sign in button and input your Whoop user information.
        2. Select "GRANT" access to your user data 
        3. You will be redirected, return to the oauth page. 
        4. Click on the url bar, and select the code between code= until &scope.
        5. Return to the Whoop & Diet APP and paste the copied code into the form.
        6. Enjoy your activity breakdown and diet recommendations. 
    ''')

with st.form("login_form"):
    whoop_token = st.text_input("Enter your Whoop authorization code", type="password")
    submitted = st.form_submit_button("Sign In")

## TRANSLATE ERROR MESSAGES TO ENGLISH - will need to delete the st.dataframe before finishing the app  
if submitted:
    if whoop_token:
        st.success("✅ Token received. Connecting to Whoop API...")
        client_id = st.secrets["client_id"]
        client_secret = st.secrets["client_secret"]
        redirect_uri = st.secrets["redirect_uri"]
        authorization_code = whoop_token

        token_url = 'https://api.prod.whoop.com/oauth/oauth2/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'code': authorization_code
        }

        response = requests.post(token_url, data=data)
        access_token = response.json().get('access_token')

        if access_token:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            # Recovery
            url_recovery = 'https://api.prod.whoop.com/developer/v1/recovery?limit=25'
            response_recovery = requests.get(url_recovery, headers=headers)
            if response_recovery.status_code == 200:
                recovery = pd.json_normalize(response_recovery.json()['records'], sep='_')
                st.session_state['recovery'] = recovery
                st.markdown("### Datos de recuperación")
                st.dataframe(recovery)
            else:
                st.error("❌ Error al obtener datos de recuperación")

            # Cycles
            url_cycles = 'https://api.prod.whoop.com/developer/v1/cycle?limit=7'
            response_cycles = requests.get(url_cycles, headers=headers)
            if response_cycles.status_code == 200:
                cycles = pd.json_normalize(response_cycles.json()['records'], sep='_')
                st.session_state['cycles'] = cycles
                st.markdown("### Cycle Data")
                st.dataframe(cycles)
            else:
                st.error("❌ Error al obtener datos de ciclos")

            # Workouts
            url_workouts = 'https://api.prod.whoop.com/developer/v1/activity/workout?limit=25'
            response_workouts = requests.get(url_workouts, headers=headers)
            if response_workouts.status_code == 200:
                workouts = pd.json_normalize(response_workouts.json()['records'], sep='_')
                st.session_state['workouts'] = workouts
                st.markdown("### Datos de entrenamientos")
                st.dataframe(workouts)
            else:
                st.error("❌ Error al obtener datos de entrenamientos")

            # Sleep
            url_sleep = 'https://api.prod.whoop.com/developer/v1/activity/sleep?limit=7'
            response_sleep = requests.get(url_sleep, headers=headers)
            if response_sleep.status_code == 200:
                sleep = pd.json_normalize(response_sleep.json()['records'], sep='_')
                st.session_state['sleep'] = sleep
                st.markdown("### Datos de sueño")
                st.dataframe(sleep)
            else:
                st.error("❌ Error al obtener datos de sueño")

            # Measurements
            url_measurements = 'https://api.prod.whoop.com/developer/v1/user/measurement/body'
            response_measurements = requests.get(url_measurements, headers=headers)
            if response_measurements.status_code == 200:
                measurements = pd.json_normalize(response_measurements.json(), sep='_')
                st.session_state['measurements'] = measurements
                st.markdown("### Medidas corporales")
                st.dataframe(measurements)
            else:
                st.error("❌ Error al obtener datos de medidas corporales")

            # Profile
            url_profile = 'https://api.prod.whoop.com/developer/v1/user/profile/basic'
            response_profile = requests.get(url_profile, headers=headers)
            if response_profile.status_code == 200:
                profile = pd.json_normalize(response_profile.json(), sep='_')
                st.session_state['profile'] = profile
                st.markdown("### Perfil del usuario")
                st.dataframe(profile)
            else:
                st.error("❌ Error al obtener datos de perfil")

        else:
            st.error("❌ No se pudo obtener el token de acceso.")
    else:
        st.error("❌ Please enter a valid API token.")



st.divider()

recovery = st.session_state['recovery'].set_index('created_at')
profile = st.session_state['profile']
sleep = st.session_state['sleep'].set_index('start')
measurements = st.session_state['measurements']
workouts = st.session_state['workouts']
# Calculate calories
cycles = st.session_state['cycles'].set_index('start')
cycles['calories'] = cycles['score_kilojoule'] / 4.184


first_name = profile['first_name'].iloc[0] 
last_name = profile['last_name'].iloc[0]

st.title(f"Welcome, {first_name} {last_name}!")



rec_score = np.mean(recovery['score_recovery_score'])
heart_score = np.mean(recovery['score_resting_heart_rate'])
skin_temp_score = round(np.mean(recovery['score_skin_temp_celsius']),2)


def get_efficiency_feedback(metric_name, value):
    if metric_name == "recovery_score":
        if value > 60:
            return "Great!"
        elif value > 40:
            return "Okay"
        else:
            return "Poor"
    elif metric_name == "resting_heart_rate":
        if value < 50:
            return "Excellent"
        elif value < 60:
            return "Good"
        elif value < 70:
            return "Okay"
        else:
            return "Too high"
    elif metric_name == "skin_temp":
        if value < 31.0:
            return "Too low"
        elif value < 34.5:
            return "Good"
        elif value <= 35.5:
            return "Slightly elevated"
        else:
            return "Too high"
    elif metric_name == "sleep_efficiency":
        if value > 85:
            return "Excellent"
        elif value > 75:
            return "Good"
        elif value > 65:
            return "Moderate"
        else:
            return "Needs improvement"
    elif metric_name == "sleep_performance":
        if value > 85:
            return "Excellent"
        elif value > 75:
            return "Good"
        elif value > 65:
            return "Moderate"
        else:
            return "Needs improvement"
    elif metric_name == "sleep_consistency":
        if value > 85:
            return "Very consistent"
        elif value > 70:
            return "Consistent"
        else:
            return "Inconsistent"
    else:
        return "Stable"
tab1, tab2, tab3 = st.tabs(["Sleep", "Recovery", "Strain performance"])

with tab1:
    st.header("Sleep Consistency (Last 7 days)")
    sleep_eff = np.mean(sleep['score_sleep_efficiency_percentage'])
    sleep_perf = np.mean(sleep['score_sleep_performance_percentage'])
    sleep_cons = np.mean(sleep['score_sleep_consistency_percentage'])

    delta_eff = get_efficiency_feedback("sleep_efficiency", sleep_eff)
    delta_perf = get_efficiency_feedback("sleep_performance", sleep_perf)
    delta_cons = get_efficiency_feedback("sleep_consistency", sleep_cons)

    col1, col2, col3 = st.columns(3)
    col1.metric("Performance Percentage", round(sleep_perf, 2), delta=delta_perf)
    col2.metric("Consistency Percentage", round(sleep_cons, 2), delta=delta_cons)
    col3.metric("Efficiency Percentage", round(sleep_eff, 2), delta=delta_eff)

with tab2:
    st.header("Average Recovery Metrics (Last 7 days)")
    rec_score = np.mean(recovery['score_recovery_score'])
    heart_score = np.mean(recovery['score_resting_heart_rate'])
    skin_temp_score = np.mean(recovery['score_skin_temp_celsius'])

    delta_msg = get_efficiency_feedback("recovery_score", rec_score)
    delta_msg_2 = get_efficiency_feedback("resting_heart_rate", heart_score)
    delta_msg_3 = get_efficiency_feedback("skin_temp", skin_temp_score)

    col1, col2, col3 = st.columns(3)
    col1.metric("Recovery Score", round(rec_score, 2), delta=delta_msg)
    col2.metric("Resting Heart Rate Score", round(heart_score, 2), delta=delta_msg_2)
    col3.metric("Skin Temperature Score", round(skin_temp_score, 2), delta=delta_msg_3)

    st.markdown("### Recovery Score over the last days")
    st.bar_chart(recovery['score_recovery_score'])

with tab3:
    st.header("Average Strain Overview (Last 7 days)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Strain Score", round(np.mean(cycles['score_strain']),2), delta="High")
    col2.metric("Max Heart Rate", round(np.max(cycles['score_max_heart_rate']),2), delta="Max")
    col3.metric("Average Heart Rate", round(np.mean(cycles['score_average_heart_rate']),2), delta="AVG")
    st.markdown("### Strain Score over the last days")
    st.line_chart(cycles['score_strain'])
    st.markdown("### Calories burned over the last days")
    st.bar_chart(cycles['calories'])



SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
SENDGRID_SENDER = st.secrets["SENDGRID_SENDER"]

def send_summary_email(recipient_email, name, sleep_avg, recovery_avg, strain_avg, recipes, goal, category):
    ingredients_list = ""
    for meal in recipes:
        meal_details = requests.get(f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal['idMeal']}").json()
        meal_info = meal_details['meals'][0]
        ingredients = [f"{meal_info[f'strMeasure{i}']} {meal_info[f'strIngredient{i}']}".strip()
                       for i in range(1, 21)
                       if meal_info[f'strIngredient{i}']]
        ingredients_formatted = "\n".join(ingredients)
        ingredients_list += f"\n\n{meal['strMeal']}:\n{ingredients_formatted}"

    content = f"""
Hi {name},

Here's your health and nutrition summary:

🔹 Sleep Score (avg): {sleep_avg:.2f}
🔹 Recovery Score (avg): {recovery_avg:.2f}
🔹 Strain Score (avg): {strain_avg:.2f}

Based on your selected diet goal ({goal}), here are 5 meal suggestions from the {category} category with ingredients:

{ingredients_list}

Stay healthy!
"""

    message = Mail(
        from_email=SENDGRID_SENDER,
        to_emails=recipient_email,
        subject="📝 Your Health & Nutrition Summary",
        plain_text_content=content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(e)
        return False






goal_categories = {
    "Cut": ["Seafood", "Vegetarian", "Side"],
    "Maintenance": ["Chicken", "Pasta", "Miscellaneous"],
    "Bulk": ["Beef", "Lamb", "Pork"]
}

st.header(" Select Your Diet Goal")
goal = st.radio("Choose your goal:", list(goal_categories.keys()), horizontal=True)

user_email = st.text_input("📧 Enter your email to receive a summary and recipes' ingredients. (Send button, at the end of the recipes)", "")


if goal:
    category = st.selectbox("Select a food category:", goal_categories[goal])

    def get_random_meals_from_category(category, n=5):
        res = requests.get(f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}").json()
        meals = res['meals']
        return random.sample(meals, min(n, len(meals))) if meals else []

    st.markdown(f"###  Meals for **{goal}** goal in category **{category}**")

    meals = get_random_meals_from_category(category, n=5)

    if not meals:
        st.warning("No meals found for this category.")
    else:
        for meal in meals:
            st.subheader(meal['strMeal'])
            st.image(meal['strMealThumb'], width=300)

            # Get detailed info
            details = requests.get(f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal['idMeal']}").json()
            info = details['meals'][0]

            st.write(info['strInstructions'][:400] + "...")
            st.markdown(f"[Full Recipe]({info['strSource'] or 'https://www.themealdb.com'})")
            st.divider()

    if user_email:
        send = st.button("📤 Send me this by email")

        if send:
            sleep_avg = np.mean(sleep['score_sleep_performance_percentage'])
            recovery_avg = np.mean(recovery['score_recovery_score'])
            strain_avg = np.mean(cycles['score_strain'])
            full_name = f"{first_name} {last_name}"

            email_sent = send_summary_email(
                user_email,
                full_name,
                sleep_avg,
                recovery_avg,
                strain_avg,
                meals,
                goal,
                category
            )

            if email_sent:
                st.success("📬 Summary email sent successfully!")
            else:
                st.error("❌ Failed to send the email. Please check your SendGrid settings.")
    else:
        st.info("💡 Enter your email above to enable the send button.")
