import socket
import threading

# Define the A2A message structure
class A2AMessage:
    def __init__(self, sender, receiver, content):
        """
        Initializes an A2A message.

        Args:
            sender (str): The sender's identifier.
            receiver (str): The receiver's identifier.
            content (str): The message content.
        """
        self.sender = sender
        self.receiver = receiver
        self.content = content

    def __str__(self):
        """
        Returns a string representation of the A2A message.  Added formatting for better readability.
        """
        return f"Sender: {self.sender}, Receiver: {self.receiver}, Content: {self.content}"

    def serialize(self):
        """
        Serializes the A2A message into a string for transmission.  Uses a simple comma-separated format.
        """
        return f"{self.sender},{self.receiver},{self.content}"

    @staticmethod
    def deserialize(data):
        """
        Deserializes a string into an A2A message object. Handles potential errors in the data.

        Args:
            data (str): The string to deserialize.

        Returns:
            A2AMessage: The deserialized message, or None on error.
        """
        try:
            parts = data.split(",", 2)  # Split only at the first two commas
            if len(parts) == 3:
                return A2AMessage(parts[0], parts[1], parts[2])
            else:
                print(f"Error: Invalid message format: {data}") #error message
                return None # Explicitly return None for error handling
        except Exception as e:
            print(f"Error deserializing message: {e}, Data: {data}")
            return None

class A2AProtocol:
    def __init__(self, agent_name, host, port):
        """
        Initializes the A2A protocol handler.

        Args:
            agent_name (str): The name of the agent using this protocol.
            host (str): The host address to listen on or connect to.
            port (int): The port number to listen on or connect to.
        """
        self.agent_name = agent_name
        self.host = host
        self.port = port
        self.socket = None
        self.on_message_received = None  # Callback for received messages
        self.running = False

    def start_server(self):
        """
        Starts a server to listen for incoming A2A messages.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)  # Listen for one connection at a time for simplicity
        print(f"{self.agent_name} Server started on {self.host}:{self.port}")
        self.running = True

        def server_loop():
            """
            Main loop for the server to accept connections and handle messages.
            """
            while self.running:
                try:
                    conn, addr = self.socket.accept()
                    print(f"Connection from {addr}")
                    self.handle_connection(conn) #moved handle_connection to its own function
                except socket.error as e:
                    if self.running: #check if the server is still supposed to be running
                        print(f"Socket error: {e}")
                    break  # Exit the loop on socket error
                except Exception as e:
                    print(f"Error in server loop: {e}")

        self.server_thread = threading.Thread(target=server_loop)
        self.server_thread.daemon = True  # Allow the program to exit even if this thread is running
        self.server_thread.start()

    def handle_connection(self, connection):
        """Handles a single connection"""
        try:
            while self.running:
                data = connection.recv(1024).decode()
                if not data:
                    break  # Connection closed by client
                message = A2AMessage.deserialize(data)
                if message:
                    print(f"{self.agent_name} received: {message}")
                    if self.on_message_received:
                        self.on_message_received(message)
                else:
                    print(f"{self.agent_name} Could not deserialize message")
        except socket.error as e:
            print(f"Socket error: {e}")
        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            connection.close()

    def connect(self, receiver_host, receiver_port):
        """
        Connects to a server to send A2A messages.

        Args:
            receiver_host (str): The host address of the server to connect to.
            receiver_port (int): The port number of the server to connect to.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((receiver_host, receiver_port))
            print(f"{self.agent_name} connected to {receiver_host}:{receiver_port}")
        except socket.error as e:
            print(f"{self.agent_name} failed to connect: {e}")
            self.socket = None  # Reset the socket on failure

    def send_message(self, message):
        """
        Sends an A2A message.  Checks if the socket is connected.

        Args:
            message (A2AMessage): The message to send.
        """
        if self.socket:
            try:
                serialized_message = message.serialize()
                self.socket.sendall(serialized_message.encode())
                print(f"{self.agent_name} sent: {message}")
            except socket.error as e:
                print(f"{self.agent_name} error sending message: {e}")
                self.socket = None  # Reset the socket on error.  Important for client to reconnect
        else:
            print(f"{self.agent_name} not connected.  Cannot send message.")

    def stop(self):
        """
        Stops the server or client, closing the socket and stopping the thread.
        """
        self.running = False #set running to false
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except socket.error as e:
                print(f"{self.agent_name} error closing socket: {e}")
            self.socket = None
        if hasattr(self, 'server_thread') and self.server_thread.is_alive():
            self.server_thread.join()
        print(f"{self.agent_name} stopped.")

if __name__ == "__main__":
    # Example usage:
    agent1 = A2AProtocol("Agent1", "localhost", 8000)
    agent2 = A2AProtocol("Agent2", "localhost", 8001)

    def handle_message_agent1(message):
        print(f"Agent1 received message: {message}")
        # agent1.send_message(A2AMessage("Agent1", "Agent2", "Reply from Agent1")) # Removed to prevent infinite loop

    def handle_message_agent2(message):
        print(f"Agent2 received message: {message}")
        agent2.send_message(A2AMessage("Agent2", "Agent1", "Reply from Agent2"))

    agent1.on_message_received = handle_message_agent1
    agent2.on_message_received = handle_message_agent2

    agent1.start_server()  # Start Agent1 as a server
    agent2.connect("localhost", 8000) # Agent 2 connects to Agent 1's server.

    # Wait for the server to start before sending a message.  Added a short delay.
    import time
    time.sleep(1)
    agent2.send_message(A2AMessage("Agent2", "Agent1", "Hello from Agent2"))

    # Keep the main thread alive to allow the server thread to run.  Reduced sleep time.
    time.sleep(5)

    agent1.stop()
    agent2.stop()
