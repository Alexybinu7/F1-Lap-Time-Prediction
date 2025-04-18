# -*- coding: utf-8 -*-
"""F1 Lap Time Predictor(LSTM).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/14uOCwNXhxR7j_2_1o4G5r1xPP9KWxy1K
"""

!pip install fastf1

import fastf1
from fastf1.core import Laps
import pandas as pd
import os

# ✅ Create the cache directory if it doesn't exist
os.makedirs('/content/f1_cache', exist_ok=True)

# Now enable the cache
fastf1.Cache.enable_cache('/content/f1_cache')

# Enable cache (to avoid downloading every time)
fastf1.Cache.enable_cache('/content/f1_cache')  # or any folder you want

# Load the Monza 2023 race
session = fastf1.get_session(2023, 'Monza', 'R')
session.load()

# Filter for Verstappen
laps_verstappen = session.laps.pick_driver('VER')

# Save to CSV
laps_verstappen.to_csv('Verstappen_Monza_2023.csv', index=False)

# Optional: Show first few rows
print(laps_verstappen[['LapNumber', 'LapTime', 'Compound', 'TyreLife', 'FreshTyre']].head())

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import fastf1

# Load session data (assuming you have a session loaded, e.g., "italian_grand_prix")
session = fastf1.get_session(2023, 'Italian Grand Prix', 'R')
session.load()

# Extract relevant data from the session
df = session.laps

# Handle missing data by filling missing values with the median
df['SpeedI1'] = df['SpeedI1'].fillna(df['SpeedI1'].median())
df['SpeedFL'] = df['SpeedFL'].fillna(df['SpeedFL'].median())
df['SpeedST'] = df['SpeedST'] = df['SpeedST'].fillna(df['SpeedST'].median())

# Convert sector times to seconds (if they are in timedelta format)
df['Sector1Time'] = df['Sector1Time'].dt.total_seconds()
df['Sector2Time'] = df['Sector2Time'].dt.total_seconds()
df['Sector3Time'] = df['Sector3Time'].dt.total_seconds()

# Optionally convert categorical columns (like 'Compound' for tire type) to numerical values
df['Compound'] = pd.Categorical(df['Compound'])
df['Compound'] = df['Compound'].cat.codes

# Select features for LSTM (e.g., Speed, Sector Times, TyreLife, Compound, Position)
features = ['SpeedI1', 'SpeedFL', 'SpeedST', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'TyreLife', 'Compound', 'Position']

# Ensure no missing values in the selected features
df = df.dropna(subset=features)

# Normalize the selected features
scaler = StandardScaler()
df[features] = scaler.fit_transform(df[features])

# Prepare sequences for LSTM
sequence_length = 10  # Number of previous laps to use as input for prediction
X, y = [], []

for i in range(sequence_length, len(df)):
    X.append(df[features].iloc[i-sequence_length:i].values)
    y.append(df['LapTime'].iloc[i].total_seconds())  # Assuming we're predicting LapTime (in seconds)

X = np.array(X)
y = np.array(y)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Now X_train, X_test, y_train, y_test are ready for use in an LSTM model

# Print the shapes of the prepared data
print("X Shape:", X.shape)
print("y Shape:", y.shape)

# If you're ready to train the LSTM model, you can proceed with the following (e.g., using Keras):

# from keras.models import Sequential
# from keras.layers import LSTM, Dense, Dropout

# Define the LSTM model
# model = Sequential()
# model.add(LSTM(64, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])))
# model.add(Dropout(0.2))
# model.add(Dense(1))
# model.compile(optimizer='adam', loss='mean_squared_error')

# # Train the model
# model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

# You can later evaluate the model, make predictions, etc.

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split

# Split data into train and test sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Build LSTM Model
model = Sequential()

# LSTM Layer - First LSTM layer with dropout
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.2))

# LSTM Layer - Second LSTM layer
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))

# Dense Layer - Fully connected layer
model.add(Dense(units=1))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
history = model.fit(X_train, y_train, epochs=20, batch_size=64, validation_data=(X_test, y_test))

# Evaluate the model on the test set
test_loss = model.evaluate(X_test, y_test)

print(f"Test Loss: {test_loss}")

# Predict lap times on the test set
predictions = model.predict(X_test)

# Optionally, you can visualize the predictions vs actual values
import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))
plt.plot(y_test, label='True Lap Times')
plt.plot(predictions, label='Predicted Lap Times')
plt.legend()
plt.show()

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt

# Assuming X_train, X_test, y_train, y_test are already defined
# If not, load your data and split accordingly

# Feature Scaling (for both X and y)
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
X_test_scaled = scaler.transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)

# Scale y (target variable)
y_scaler = MinMaxScaler()
y_train_scaled = y_scaler.fit_transform(y_train.reshape(-1, 1))
y_test_scaled = y_scaler.transform(y_test.reshape(-1, 1))

# Define the model with more layers and units
model = Sequential()

# First LSTM layer with more units and return sequences
model.add(LSTM(units=100, return_sequences=True, input_shape=(X_train_scaled.shape[1], X_train_scaled.shape[2])))
model.add(Dropout(0.2))

# Second LSTM layer
model.add(LSTM(units=100, return_sequences=True))
model.add(Dropout(0.2))

# Third LSTM layer
model.add(LSTM(units=100))
model.add(Dropout(0.2))

# Dense layer for output
model.add(Dense(units=1))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Early stopping to avoid overfitting
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train the model
history = model.fit(X_train_scaled, y_train_scaled,
                    epochs=50, batch_size=64,
                    validation_data=(X_test_scaled, y_test_scaled),
                    callbacks=[early_stopping])

# Plotting training and validation loss
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Making predictions and inversing scaling for y
predictions_scaled = model.predict(X_test_scaled)
predictions = y_scaler.inverse_transform(predictions_scaled)

# Inverse scaling for true values of y
y_test_original = y_scaler.inverse_transform(y_test_scaled)

# Evaluating the model with Mean Absolute Error
mae = mean_absolute_error(y_test_original, predictions)
print(f"Mean Absolute Error: {mae}")

# Optionally, plot the predictions against the true values
plt.plot(y_test_original, label='True Values')
plt.plot(predictions, label='Predictions')
plt.xlabel('Samples')
plt.ylabel('Lap Time')
plt.legend()
plt.show()