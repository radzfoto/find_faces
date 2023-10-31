import tensorflow as tf
import numpy as np

# Set log level to INFO
tf.get_logger().setLevel('INFO')

# Define a simple model
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Generate some random data
data = np.random.random((1000, 32))
labels = np.random.randint(10, size=(1000, 1))

# Train the model for a single epoch
history = model.fit(data, labels, epochs=1)
