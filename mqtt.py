import tkinter as tk
import paho.mqtt.client as mqtt

class HyperTerminal:
    def __init__(self, master):
        self.master = master
        self.master.title("HyperTerminal")
        
        self.connect_button = tk.Button(master, text="Connect", command=self.connect_to_mqtt)
        self.connect_button.pack()

        self.disconnect_button = tk.Button(master, text="Disconnect", command=self.disconnect_from_mqtt, state="disabled")
        self.disconnect_button.pack()

        self.message_entry = tk.Entry(master)
        self.message_entry.pack()
        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack()

        self.topic_buttons = {}
        topics = ["topic1", "topic2", "topic3"] # Change topics as per your requirements
        for topic in topics:
            button = tk.Button(master, text=topic, command=lambda t=topic: self.subscribe_to_topic(t))
            button.pack()
            self.topic_buttons[topic] = button

        self.client = None

    def connect_to_mqtt(self):
        # self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("192.168.1.94", 1883, 60)
        self.client.loop_start()

    def send_message(self):
        message = self.message_entry.get()
        if self.client:
            self.client.publish('prism/board1/switch1', message)
            print("Message sent:", message)
        else:
            print("Not connected to MQTT Broker yet")

    def disconnect_from_mqtt(self):
        if self.client:
            self.client.disconnect()
            self.client.loop_stop()
            self.connect_button["state"] = "active"
            self.disconnect_button["state"] = "disabled"

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker")
            self.connect_button["state"] = "disabled"
            self.disconnect_button["state"] = "active"
        else:
            print("Failed to connect to MQTT Broker")

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))

    def subscribe_to_topic(self, topic):
        if self.client:
            self.client.subscribe(topic)
            print("Subscribed to topic:", topic)
        else:
            print("Not connected to MQTT Broker yet")

def main():
    root = tk.Tk()
    app = HyperTerminal(root)
    root.mainloop()

if __name__ == "__main__":
    main()