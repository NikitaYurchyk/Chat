# TCP Chat

## Overview
TCP Chat is a real-time chat application developed using Python over TCP/IP, offering a platform for instant messaging and network communication. This application incorporates basic user authentication, private messaging, and supports multiple concurrent connections through both threaded and async-await programming models. With SQLite integration, it ensures persistent storage and retrieval of private messages, making it an efficient and robust solution for online communication.

## Features
- **Instant Messaging**: Send and receive messages in real-time over a network.
- **User Authentication**: Basic authentication system for user identification.
- **Private Messaging**: Securely send messages to individual users.
- **Concurrent Connections**: Support for multiple users connected simultaneously through threaded and async-await implementations.
- **Persistent Storage**: SQLite database for storing and retrieving private messages.

## Getting Started

### Prerequisites
- Python 3.x
- SQLite

### Running the Application
1. **Start the Server**
   - Navigate to the application directory and run the server using:
     ```
     python .server
     ```
2. **Start the Client**
   - Open a new terminal session and start the client with:
     ```
     python .client
     ```

### Usage
- **View Online Users**: Type `!users` to display all currently online users.
- **Send Private Messages**: Use `@<receiver> <message>` to send a private message to another user.
- **View Message History**: Type `!history` to retrieve all messages you've received.
- **Quit**: Enter `!quit` to exit the chat application.

