
### Requirements
It is required that you have a mqtt broker installed on your machine. 
Head over to `docs/mqtt_for_online_students.md` for installing Mosquitto MQTT broker.

If you have mosquitto installed, you can run it by opening a command prompt (in Windows)
and run `mosquitto -d`.

Alternatively, if you have docker on your machine, you can run a container with the 
following command:
`docker run -d --name mqtt-mosquitto -it -p 1883:1883 -d eclipse-mosquitto`

### Installation and Running
1. Clone this repository to your local machine: `git clone https://github.com/ca20110820/at3-carpark.git`.
2. Go to the local repository: `cd at3-carpark/`.
3. Create a Virtual Environment: `python -m venv .venv`.
4. Activate the VENV:
    * Git Bash: `source ./.venv/Scripts/activate`
    * Command Prompt: `.\.venv\Scripts\activate`
5. Install the requirements and smartpark `pip install -e .`
6. Run the application: `python smartpark`