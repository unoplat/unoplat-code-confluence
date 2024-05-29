# Codebase Overview

## System Overview

- **Name**: [System Name]
- **Description**: [Brief description of the system in terms of responsibilities and interactions
Both internal/external (External includes calls to databases/message brokers/external api services)]

## High-Level Architecture

- **Components**: [Fill in: Try to break down the system in components - Components can be of two types. One internal(based on system name) and all other will be external. External can be anything like database, message broker, external api services etc.]
  - **Component 1**: [Fill in: Description of Component 1]
    - **Responsibilities**: [Fill in: What does this component do? if it is a internal one then include all interactions in terms of what is the trigger (rest/grpc etc) and how they are processed with the flow including precise class names based on nodenames shared from context. If it is an external one then include all interactions in terms of what is the trigger (rest/grpc etc) and how they are processed.]
    - **Interactions**: [Fill in: How does this component interact with other components?]
  - **Component 2**: [Fill in: Description of Component 2]
    - **Responsibilities**: [Fill in: What does this component do? if it is a internal one then include all interactions in terms of what is the trigger (rest/grpc etc) and how they are processed with the flow including precise class names based on nodenames shared from context. If it is an external one then include all interactions in terms of what is the trigger (rest/grpc etc) and how they are processed.]
    - **Interactions**: [Fill in: How does this component interact with other components?]
