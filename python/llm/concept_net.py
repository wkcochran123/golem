import tensorflow as tf
from tensorflow.keras.layers import Input, Reshape, Conv1D, GlobalAveragePooling1D
from tensorflow.keras.layers import LSTM, Dense, Concatenate
from tensorflow.keras.models import Model

class ConceptNet():
    def __init__(self, dim, out_len):
        super().__init__()

        self.IN_SIZE = dim
        self.OUT_SIZE = out_len

        # Input: 4096 concept EMAs
        input_tensor = Input(shape=(self.IN_SIZE,), name='concept_ema')

        # --- CNN branch ---
        x_cnn = Reshape((self.IN_SIZE, 1))(input_tensor)
        x_cnn = Conv1D(filters=64, kernel_size=5, strides=2, activation='relu')(x_cnn)
        x_cnn = Conv1D(filters=128, kernel_size=5, strides=2, activation='relu')(x_cnn)
        x_cnn = GlobalAveragePooling1D()(x_cnn)

        # --- LSTM branch ---
        x_lstm = Reshape((self.IN_SIZE, 1))(input_tensor)
        x_lstm = tf.keras.layers.Bidirectional(LSTM(128))(x_lstm)

        # --- MLP branch ---
        x_mlp = Dense(512, activation='relu')(input_tensor)
        x_mlp = Dense(256, activation='relu')(x_mlp)

        # --- Concatenate all paths ---
        x = Concatenate()([x_cnn, x_lstm, x_mlp])
        x = Dense(1024, activation='relu')(x)
        output = Dense(self.OUT_SIZE, activation=None, name='logits')(x)

        # Build model
        self.model = Model(inputs=input_tensor, outputs=output)
        self.model.compile(optimizer='adam', loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True))


    def predict(self, x):
        return self.model.predict(x)

	def backprop_reward(self, input_vector, reward, learning_rate=1e-4):
		"""
		Backpropagates a scalar reward from a single input example.
		"""
		input_tensor = tf.convert_to_tensor(input_vector, dtype=tf.float32)

		with tf.GradientTape() as tape:
			tape.watch(self.model.model.trainable_weights)
			logits = self.model.model(input_tensor, training=True)
			# reduce logits to a single scalar using mean or other aggregator
			output_scalar = tf.reduce_mean(logits)
			# you want to minimize the difference between predicted mood and observed
			loss = tf.square(output_scalar - reward)

		gradients = tape.gradient(loss, self.model.model.trainable_weights)
		optimizer = tf.keras.optimizers.Adam(learning_rate)
		optimizer.apply_gradients(zip(gradients, self.model.model.trainable_weights))

		return loss.numpy()

