# Test Plan for Distributed IoT Classroom Management System

## Introduction
This document outlines the testing strategy for the Distributed IoT Classroom Management System, focusing on correctness, reliability, and robustness of the core components.

We have implemented unit testing for the key areas below using mocks. Conducting tests in isolation of other components enables us to be sure of a function/class's functionality and act as documentation or a sanity check for for debugging the system. 

The tests are run automatically via GitHub actions to ensure each pull request and commit are run through the extensive unit test suite, preventing integration errors between feature branches.

---

## Scope of Testing
Key areas include:

- User input validation  
- Authentication and booking logic  
- MQTT and Socket communication  
- Room state transitions  
- Error and exception handling 
<b>
- QR Code Login
</b>

---

## Test Execution
- Tests are written with **pytest** and organized in [`tests/unit`](./tests/unit).  
- Run locally or via GitHub Actions.  
- Coverage reported with `pytest --cov`.
- Detailed pytest report with `pytest --cov -v`. 

