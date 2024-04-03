import assemblyai as aai
from elevenlabs import generate, stream
from openai import OpenAI

#install "mpv" using chocolately on windows - required for reading streaming audio

#create ai assistant class
class AI_Assitant:
    def __init__(self):
        aai.settings.api_key ="ASSEMBLY_API_KEY"
        self.openai_client = OpenAI(api_key="OPEN_AI_API_KEY")
        self.elevenlabs_api_key = "ELEVENLABS_API_KEY"

        #transcribe object
        self.transcriber = None

        #Prompt
        self.full_transcript = [
            {
                "role": "system", 
                "content": "You are a receptionist at a dental clinic. Be resourceful and efficient"
            }
        ]

    #--- ASSEMBLY AI TRANSCRIPTION
        
    #start the transcription
    def start_transcription(self):
        #create a transcriber and define the class transcriber with it
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate= 16000,
            on_data= self.on_data,
            on_error= self.on_error,
            on_open= self.on_open,
            on_close= self.on_close,
            end_utterance_silence_threshold= 1000
        )
        
        #connect
        self.transcriber.connect()

        #connect mic to the assembly api
        microphone_stream =  aai.extras.MicrophoneStream(sample_rate=16000)
        self.transcriber.stream(microphone_stream)
    


    #stop the transcription
    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None
        

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        #print("Session ID:", session_opened.session_id)
        return

    #deals with the data
    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript):
            #print(transcript.text, end="\r\n")
            #send the data
            self.generate_ai_response(transcript)
        else:
            print(transcript.text, end="\r")


    def on_error(self, error: aai.RealtimeError):
        #print("An error occured:", error)
        return


    def on_close(self):
        #print("Closing Session")
        return

    
    #--- PASS REAL_TIME TRANSCRIPT DATA TO OPENAI

    def generate_ai_response(self, transcript):

        #stop the transcription stream while sending the data
        self.stop_transcription()

        #append to the transcription object, the new data
        self.full_transcript.append({"role": "user", "content": transcript.text})
        print(f"\nPatient: {transcript.text}", end="\r\n")

        #pass the data to openAi api
        response = self.openai_client.chat.completions.create(
            model= "gpt-3.5-turbo",
            messages = self.full_transcript
        )

        #get the response from openAi
        ai_response = response.choices[0].message.content

        #generate the audio based on the response from openAi
        self.generate_audio(ai_response)

        #restart the transcription again
        self.start_trascription()


    #--- GENERATE AUDIO
    def generate_audio(self, text):

        #add the text to the transcript
        self.full_transcript.append({"role":"assistant", "content": text})

        print(f"\nAI Assitant: {text}")

        #send data to elevenlabs api
        audio_stream = generate(
            api_key=self.elevenlabs_api_key,
            text= text,
            voice= "Rachel",
            stream= True
        )

        stream(audio_stream)

greeting = "Thank you for calling, My name is Sandy, how may I assist you today?"
ai_assitant = AI_Assitant()
ai_assitant.generate_audio(greeting)
ai_assitant.start_transcription()
