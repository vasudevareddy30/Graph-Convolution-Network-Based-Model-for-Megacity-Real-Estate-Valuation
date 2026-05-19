from django.shortcuts import render
from .models import UserPrediction
import torch
import pickle
import numpy as np
from torch_geometric.data import Data
from torch_geometric.utils import dense_to_sparse
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

# Create your views here.
def userhome(request):
    user = request.user
    return render(request, 'User/userhome.html', {'user': user})

# Define Graph-based Regression Model with Attention
class A_SRGCNN(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(A_SRGCNN, self).__init__()
        self.conv1 = GCNConv(input_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.attention = nn.Linear(hidden_dim, 1)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = F.relu(self.conv1(x, edge_index))
        attn_weights = torch.sigmoid(self.attention(x))
        x = attn_weights * x  # Applying attention
        x = F.relu(self.conv2(x, edge_index))
        x = self.fc(x)
        return x

# Load encoders and scaler
with open("model/label_encoders.pkl", "rb") as f:
    label_encoders = pickle.load(f)

with open("model/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# Load trained model
input_dim = len(scaler.mean_)  # Get number of input features
model = A_SRGCNN(input_dim=input_dim, hidden_dim=64, output_dim=1)
model.load_state_dict(torch.load("model/ASRGCNN_model.pth"))
model.eval()

def predict(input_data):
    """Function to predict house price given custom input"""
    input_data_scaled = scaler.transform(input_data)
    input_tensor = torch.tensor(input_data_scaled, dtype=torch.float32)

    # Create a self-looping adjacency matrix for the single input
    input_adj_matrix = torch.ones((1, 1))
    input_edge_index, _ = dense_to_sparse(input_adj_matrix)

    input_data_obj = Data(x=input_tensor, edge_index=input_edge_index)

    with torch.no_grad():
        prediction = model(input_data_obj)

    return prediction.item()

def userpredict(request):
    if request.method == "POST":
        # Maintain the correct feature order
        feature_order = [
            'area', 'bedrooms', 'bathrooms', 'stories',
            'mainroad', 'guestroom', 'basement', 'hotwaterheating',
            'airconditioning', 'parking', 'prefarea', 'furnishingstatus'
        ]

        input_data = []
        user_inputs = {}

        for feature in feature_order:
            value = request.POST.get(feature, "")
            user_inputs[feature] = value

            if feature in label_encoders:
                if value in label_encoders[feature].classes_:
                    encoded_value = label_encoders[feature].transform([value])[0]
                else:
                    encoded_value = 0  # Default encoding if value not found
            else:
                try:
                    encoded_value = float(value)
                except ValueError:
                    encoded_value = 0  # Default for invalid numeric input

            input_data.append(encoded_value)

        input_data = np.array(input_data).reshape(1, -1)
        predicted_price = predict(input_data)

        # Save to database
        UserPrediction.objects.create(user_input=user_inputs, predicted_price=predicted_price)

        return render(request, 'User/userpredict.html', {'predicted_price': predicted_price})

    return render(request, 'User/userpredict.html')
