# a2a_client.py

import socket
import json
import struct # For packing and unpacking binary data
import time

# --- Configuration ---
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 40808
BUFFER_SIZE = 1024

# --- Mock Security Functions (Placeholders) ---
def perform_client_handshake(sock):
    """
    Simulates the client side of an A2A handshake.
    """
    print("[Client] Starting handshake...")
    client_hello = {"message": "A2A_CLIENT_HELLO", "client_id": "PythonClient_123"}
    client_hello_data = json.dumps(client_hello).encode('utf-8')

    # Send length of the message first, then the message
    sock.sendall(struct.pack('>I', len(client_hello_data)))
    sock.sendall(client_hello_data)
    print("[Client] Sent client hello.")

    # Wait for server acknowledgment
    print("[Client] Waiting for server acknowledgment...")
    server_ack_packed_len = sock.recv(4) # Expect 4 bytes for length
    if not server_ack_packed_len:
        print("[Client] Server disconnected before sending ack length.")
        return False
        
    msg_len = struct.unpack('>I', server_ack_packed_len)[0]
    server_ack_data = sock.recv(msg_len)
    if not server_ack_data:
        print("[Client] Server disconnected before sending ack data.")
        return False

    server_ack = json.loads(server_ack_data.decode('utf-8'))
    print(f"[Client] Received server ack: {server_ack}")

    if server_ack.get("message") == "A2A_SERVER_ACK" and server_ack.get("status") == "OK":
        # In a real scenario, session keys would be derived/exchanged here.
        print("[Client] Mock Handshake successful. Session 'secured'.")
        return True
    else:
        print("[Client] Server acknowledgment failed or invalid.")
        return False

def encrypt_message(data, session_key=None):
    """
    Placeholder for message encryption.
    In a real A2A protocol, this would use the established session key.
    """
    # For this example, we just convert dict to JSON bytes.
    print("[Client] 'Encrypting' message...")
    return json.dumps(data).encode('utf-8')

def decrypt_response(encrypted_data, session_key=None):
    """
    Placeholder for message decryption.
    """
    print("[Client] 'Decrypting' response...")
    try:
        return json.loads(encrypted_data.decode('utf-8'))
    except json.JSONDecodeError:
        print("[Client] Error: Could not decode response as JSON.")
        return None
    except Exception as e:
        print(f"[Client] Error during 'decryption': {e}")
        return None

def send_framed_message(sock, message_bytes):
    """
    Sends a message prefixed with its length.
    """
    sock.sendall(struct.pack('>I', len(message_bytes)))
    sock.sendall(message_bytes)

def receive_framed_message(sock):
    """
    Receives a message prefixed with its length.
    """
    packed_msg_len = sock.recv(4)
    if not packed_msg_len:
        return None
    msg_len = struct.unpack('>I', packed_msg_len)[0]
    
    data = b''
    while len(data) < msg_len:
        packet = sock.recv(min(msg_len - len(data), BUFFER_SIZE))
        if not packet:
            return None
        data += packet
    return data

# --- Main Client Logic ---
def send_a2a_message(message_content):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            print(f"[Client] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
            s.connect((SERVER_HOST, SERVER_PORT))
            print("[Client] Connected.")

            # 1. Perform Handshake
            if not perform_client_handshake(s):
                print("[Client] Handshake failed. Exiting.")
                return

            # 2. Prepare and Encrypt Message
            app_message = {
                "type": "data_exchange",
                "payload": {
                    "command": "send_info",
                    "content": message_content,
                    "timestamp": time.time()
                }
            }
            encrypted_message = encrypt_message(app_message) # session_key would be used here

            # 3. Send Message
            print(f"[Client] Sending 'encrypted' message: {encrypted_message[:60]}...")
            send_framed_message(s, encrypted_message)
            print("[Client] Message sent.")

            # 4. Receive and Decrypt Response
            print("[Client] Waiting for response...")
            encrypted_response_data = receive_framed_message(s)

            if encrypted_response_data:
                print(f"[Client] Received 'encrypted' response: {encrypted_response_data[:60]}...")
                response = decrypt_response(encrypted_response_data) # session_key would be used
                if response:
                    print(f"[Client] Decrypted response: {response}")
                else:
                    print("[Client] Failed to decrypt response.")
            else:
                print("[Client] No response received or server disconnected.")

        except ConnectionRefusedError:
            print(f"[Client] Connection refused. Is the server running at {SERVER_HOST}:{SERVER_PORT}?")
        except Exception as e:
            print(f"[Client] An error occurred: {e}")
        finally:
            print("[Client] Closing connection.")

if __name__ == '__main__':
    # Example usage:
    data_to_send = "Hello A2A World from Python Client!"
    send_a2a_message(data_to_send)

    print("\n--- Sending another message (demonstrates client can run multiple times) ---")
    time.sleep(1) # Small delay
    data_to_send_2 = {"value": 42, "user": "test_user"}
    send_a2a_message(data_to_send_2)