# OTT Multimedia Streaming System

A networked system for on-demand and real-time audio/video streaming using an overlay-based architecture. Developed as part of the "Network Service Engineering" course at the University of Minho.

---

## Project Overview

This project implements an **Over-the-Top (OTT)** streaming platform where media is delivered via an overlay network on top of a standard IP infrastructure.

Three key roles define the system:
- **Server** – central controller and content distributor
- **OTT Node** – intermediary nodes that forward content
- **Client** – endpoint consumers requesting media

The system uses **TCP for control communication** and **UDP for media streaming**.

---

## Features

- Overlay routing using Breadth-First Search (BFS)
- Dynamic node registration and disconnection
- Multithreaded architecture for concurrency
- Separate TCP/UDP logic for control and stream paths
- IP whitelisting and basic message encoding for security
- Stream forwarding via OTT nodes (unicast, multicast-style)

---

## Architecture

The system is composed of three main entities:

- **Server**: Acts as the central coordinator. It handles registration, topology computation (via BFS), and initiates media transmission.
- **OTT Node**: Intermediate relay node. It forwards streaming data from the server to downstream nodes or clients.
- **Client**: Endpoint that receives and consumes the stream.

### Communication Flow

- **TCP (Control Plane)**: Used for registration, topology updates, and control messages between server, OTT nodes, and clients.
- **UDP (Data Plane)**: Used for streaming media between nodes in the overlay path.


---

## 👥 Contributors

- Luís Carlos Sousa Magalhães  
- António Jorge Nande Rodrigues  
- Francisco Correia Franco


