import requests
import re
from datetime import datetime
from aura_utils import send_email, read_emails, create_calendar_event, get_calendar_events, summarize_text, draft_email, get_model

class AuraAgent:
    def __init__(self):
        self.conversation_history = []
        self.user_preferences = {"weather_location": None}
        # A mapping from intents to handler methods
        self.intent_handlers = {
            "greeting": self._handle_greeting,
            "get_weather": self._handle_weather,
            "get_time": self._handle_time,
            "summarize": self._handle_summarize,
            "schedule_meeting": self._handle_calendar_event,
            "read_calendar": self._handle_read_calendar,
            "send_email": self._handle_email,
            "read_emails": self._handle_read_emails,
            "set_location": self._handle_set_location,
            "draft_email": self._handle_draft_email,
            "unknown": self._handle_unknown,
        }

    def process_command(self, user_input):
        intent, entities = self._parse_intent(user_input)

        handler = self.intent_handlers.get(intent, self._handle_unknown)
        response = handler(user_input, **entities)

        self._update_history(intent, response)
        return response

    def _parse_intent(self, user_input):
        prompt = f"""
        Given the user input, classify the intent and extract relevant entities.
        The possible intents are: greeting, get_weather, get_time, summarize, schedule_meeting, read_calendar, send_email, read_emails, set_location, draft_email, unknown.
        Entities to extract:
        - for schedule_meeting: summary, start_time, end_time, date
        - for send_email: recipient, subject, body
        - for set_location: location
        - for summarize: text
        - for draft_email: prompt

        User input: "{user_input}"

        Respond with a JSON object with two keys: "intent" and "entities".
        """
        try:
            model = get_model()
            if not model:
                return "unknown", {"error": "Model not initialized"}
            response = model.generate_content(prompt)
            # A simple way to parse the JSON from the model's response
            import json
            parsed_response = json.loads(response.text.strip("```json\n").strip("```"))
            return parsed_response.get("intent", "unknown"), parsed_response.get("entities", {})
        except Exception:
            return "unknown", {}

    def _update_history(self, action, response):
        self.conversation_history.append((action, response))
        if len(self.conversation_history) > 5:
            self.conversation_history.pop(0)

    # Command Handlers
    def _handle_greeting(self, user_input, **entities):
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            return "Good morning! How can I help you today?"
        elif 12 <= current_hour < 18:
            return "Good afternoon! How can I help you today?"
        else:
            return "Good evening! How can I help you today?"

    def _handle_weather(self, user_input, **entities):
        location = self.user_preferences.get("weather_location")
        if not location:
            return "I don't have a location for you. Please say 'my location is <city>' to set one."

        try:
            response = requests.get(f"https://wttr.in/{location}?format=j1")
            response.raise_for_status()
            data = response.json()

            if "tomorrow" in user_input.lower():
                weather_desc = data['weather'][1]['hourly'][4]['weatherDesc'][0]['value']
                return f"Tomorrow's forecast for {location} is: {weather_desc}."
            else:
                weather_desc = data['current_condition'][0]['weatherDesc'][0]['value']
                return f"The weather in {location} is currently: {weather_desc}."
        except requests.exceptions.RequestException as e:
            return f"Sorry, I couldn't retrieve the weather. {e}"

    def _handle_time(self, user_input, **entities):
        return f"The current time is {datetime.now().strftime('%H:%M')}."

    def _handle_summarize(self, user_input, **entities):
        text = entities.get("text")
        if not text:
            return "Please provide the text you want me to summarize."
        return summarize_text(text)

    def _handle_draft_email(self, user_input, **entities):
        prompt = entities.get("prompt")
        if not prompt:
            return "Please provide a prompt for the email you want me to draft."
        return draft_email(prompt)

    def _handle_calendar_event(self, user_input, **entities):
        summary = entities.get("summary")
        start_time = entities.get("start_time")
        end_time = entities.get("end_time")
        date = entities.get("date")

        if not all([summary, start_time, end_time, date]):
            return "I couldn't understand the event details. Please provide a summary, start time, end time, and date."

        try:
            from dateutil.parser import parse

            start_datetime = parse(f"{date} {start_time}")
            end_datetime = parse(f"{date} {end_time}")

            start_time_rfc = start_datetime.isoformat()
            end_time_rfc = end_datetime.isoformat()

            return create_calendar_event(summary, start_time_rfc, end_time_rfc)
        except ValueError:
            return "I had trouble understanding the date or time. Please use a clear format like 'tomorrow at 2pm'."

    def _handle_read_calendar(self, user_input, **entities):
        events = get_calendar_events()
        if not events:
            return "No upcoming events found."
        return "Here are your upcoming events:\n- " + "\n- ".join(events)

    def _handle_email(self, user_input, **entities):
        recipient = entities.get("recipient")
        subject = entities.get("subject")
        body = entities.get("body")

        if not recipient:
            return "I need a recipient to send the email to."

        return send_email(recipient, subject, body)

    def _handle_read_emails(self, user_input, **entities):
        emails = read_emails()
        if not emails:
            return "No emails found."
        return "Here are your latest emails:\n- " + "\n- ".join(emails)

    def _handle_set_location(self, user_input, **entities):
        location = entities.get("location")
        if not location:
            return "I need a location to set."
        self.user_preferences["weather_location"] = location
        return f"Okay, I've set your preferred weather location to {location}."

    def _handle_unknown(self, user_input, **entities):
        return "I'm not sure how to help with that yet. Can you please rephrase?"
