# System Architecture

Based on the code structure and components of your project (Django backend + PyTorch GCN model), I have generated the system architecture diagrams representing how everything connects and processes information.

### 1. High-Level System Architecture
This diagram outlines the overall flow from the client side (User/Admin) through your Django application, and into the Machine Learning engine and Database.

```mermaid
graph TD
    classDef client fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef server fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;
    classDef ml fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef db fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
    classDef storage fill:#eceff1,stroke:#37474f,stroke-width:2px;

    subgraph Client ["🖥️ Client Side (Browser)"]
        U([User]) -->|Input property features| UI[User UI / HTML Forms]
        A([Admin]) -->|Manage & view history| AD[Admin UI / Dashboard]
    end

    subgraph Django_Backend ["⚙️ Django Web Server"]
        UI -->|HTTP POST Request| UR[User Application <br> views.py]
        AD -->|HTTP Requests| AR[Admins Application <br> views.py]
        
        UR --> DM[Data Preprocessing & <br> Encoding Logic]
        UR -.->|Save Prediction| DB[(SQLite Database)]
        AR -.->|Fetch History & Users| DB
    end

    subgraph Deep_Learning ["🧠 PyTorch ML Engine"]
        DM -->|Scaled Numpy Arrays| PT[Graph Construction <br> torch_geometric & Tensors]
        PT -->|Node Features & Edges| GCN[A_SRGCNN Model <br> Inference]
        GCN -->|Predicted Price| UR
    end

    subgraph Saved_Models ["📁 Saved Storage (Local)"]
        SM1[label_encoders.pkl] -.->|Load Encoders| DM
        SM2[scaler.pkl] -.->|Load Scaler| DM
        SM3[ASRGCNN_model.pth] -.->|Load Weights| GCN
    end

    class U,A,UI,AD client;
    class UR,AR,DM,PT server;
    class GCN ml;
    class DB db;
    class SM1,SM2,SM3 storage;
```

---

### 2. Machine Learning Model Architecture Flowchart
This details the exact step-by-step transformation inside your `A_SRGCNN` model as seen in your `views.py` file, showing how the raw input array becomes a price prediction.

```mermaid
flowchart TD
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef tensor fill:#fff8e1,stroke:#ff8f00,stroke-width:2px
    classDef model_layer fill:#fbe9e7,stroke:#d84315,stroke-width:2px
    classDef output fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px

    RawInput[1. Raw Form Input 1x12<br/>Area, Bedrooms, etc.] --> Encode[2. Label Encoders<br/>Convert text to numbers]
    Encode --> Scale[3. Standard Scaler<br/>Normalize values]
    
    Scale --> TensorData[4. PyTorch Tensor Conversion<br/>float32]
    TensorData --> GraphData[5. Graph Construction<br/>Dense to Sparse Adjacency Matrix]

    subgraph A_SRGCNN ["🧠 Inside A_SRGCNN PyTorch Model"]
        direction TB
        GraphData --> L1[6. GCNConv Layer 1<br/>Input to Hidden Dim 64]
        L1 --> R1[7. ReLU Activation Function]
        
        R1 --> Att[8. Attention Layer<br/>Linear Layer + Sigmoid]
        
        R1 --> Mult{9. Multiply Features<br/>by Attention Weights}
        Att --> Mult
        
        Mult --> L2[10. GCNConv Layer 2<br/>Hidden to Hidden Dim 64]
        L2 --> R2[11. ReLU Activation Function]
        
        R2 --> FC[12. Fully Connected Linear Layer<br/>Hidden to Output Dim 1]
    end
    
    FC --> FinalPrediction([13. Final Predicted House Price])

    class RawInput,Encode,Scale process
    class TensorData,GraphData tensor
    class L1,R1,Att,Mult,L2,R2,FC model_layer
    class FinalPrediction output
```
