# Round-Robin Project

## Description

This project implements a round-robin scheduling algorithm. 

The round robin API receives a request and chooses which application API instance to send the request to on a ‘round robin’ basis. This means if you have 3 instances of the application API, then the first request goes to instance 1, the second to instance 2, the third to instance 3, and so on. This cycle repeats as more requests come in, ensuring a fair distribution of requests across all instances.

## Steps to Run

1. Clone the repo:
    ```bash
    git clone https://github.com/kairules55/Round-Robin.git
    ```
2. Navigate to the project directory:
    ```bash
    cd round-robin-project
    ```
3. Run the project:
    ```bash
    python3 run.py
    ```