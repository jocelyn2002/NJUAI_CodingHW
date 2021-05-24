# 加载需要使用的函数与类
import keras.backend as k
from keras.models import Sequential
from keras.layers import Dense, Convolution2D, MaxPooling2D, Flatten
from keras.datasets import mnist
from keras.utils import np_utils
import matplotlib.pyplot as plt
import numpy as np
import abc
import logging
import six
if True:
    NUMPY_DTYPE = np.float32
    logger = logging.getLogger(__name__)
    def get_labels_np_array(preds):
        preds_max = np.amax(preds, axis=1, keepdims=True)
        y = (preds == preds_max).astype(float)
        return y
    def original_to_tanh(x_original, clip_min, clip_max, tanh_smoother=0.999999):
        x_tanh = np.clip(x_original, clip_min, clip_max)
        x_tanh = (x_tanh - clip_min) / (clip_max - clip_min)
        x_tanh = np.arctanh(((x_tanh * 2) - 1) * tanh_smoother)
        return x_tanh
    def tanh_to_original(x_tanh, clip_min, clip_max, tanh_smoother=0.999999):
        x_original = (np.tanh(x_tanh) / tanh_smoother + 1) / 2
        return x_original * (clip_max - clip_min) + clip_min
    def compute_success(classifier, x_clean, labels, x_adv, targeted=False, batch_size=1):
        adv_preds = np.argmax(classifier.predict(x_adv, batch_size=batch_size), axis=1)
        if targeted:
            rate = np.sum(adv_preds == np.argmax(labels, axis=1)) / x_adv.shape[0]
        else:
            preds = np.argmax(classifier.predict(x_clean, batch_size=batch_size), axis=1)
            rate = np.sum(adv_preds != preds) / x_adv.shape[0]

        return rate


    ABC = abc.ABC
    class Classifier(ABC):
        def __init__(self, channel_index, clip_values=None, defences=None, preprocessing=(0, 1)):
            from art.defences.preprocessor import Preprocessor

            if clip_values is not None:
                if len(clip_values) != 2:
                    raise ValueError('`clip_values` should be a tuple of 2 floats or arrays containing the allowed'
                                     'data range.')
                if np.array(clip_values[0] >= clip_values[1]).any():
                    raise ValueError('Invalid `clip_values`: min >= max.')
            self._clip_values = clip_values

            self._channel_index = channel_index
            if isinstance(defences, Preprocessor):
                self.defences = [defences]
            else:
                self.defences = defences

            if len(preprocessing) != 2:
                raise ValueError('`preprocessing` should be a tuple of 2 floats with the substract and divide values for'
                                 'the model inputs.')
            self.preprocessing = preprocessing

        @abc.abstractmethod
        def predict(self, x, logits=False, batch_size=128, **kwargs):
            raise NotImplementedError

        @abc.abstractmethod
        def fit(self, x, y, batch_size=128, nb_epochs=20, **kwargs):
            raise NotImplementedError

        def fit_generator(self, generator, nb_epochs=20, **kwargs):
            from art.data_generators import DataGenerator

            if not isinstance(generator, DataGenerator):
                raise ValueError('Expected instance of `DataGenerator` for `fit_generator`, got %s instead.'
                                 % str(type(generator)))

            for _ in range(nb_epochs):
                x, y = generator.get_batch()

                # Apply preprocessing and defences
                x_preprocessed, y_preprocessed = self._apply_preprocessing(x, y, fit=True)

                # Fit for current batch
                self.fit(x_preprocessed, y_preprocessed, nb_epochs=1, batch_size=len(x), **kwargs)

        @property
        def nb_classes(self):
            return self._nb_classes

        @property
        def input_shape(self):
            return self._input_shape

        @property
        def clip_values(self):
            return self._clip_values

        @property
        def channel_index(self):
            return self._channel_index

        @property
        def learning_phase(self):
            return self._learning_phase if hasattr(self, '_learning_phase') else None

        @abc.abstractmethod
        def class_gradient(self, x, label=None, logits=False, **kwargs):

            raise NotImplementedError

        @abc.abstractmethod
        def loss_gradient(self, x, y, **kwargs):

            raise NotImplementedError

        @property
        def layer_names(self):

            raise NotImplementedError

        @abc.abstractmethod
        def get_activations(self, x, layer, batch_size):

            raise NotImplementedError

        @abc.abstractmethod
        def set_learning_phase(self, train):

            raise NotImplementedError

        @abc.abstractmethod
        def save(self, filename, path=None):
            raise NotImplementedError

        def _apply_preprocessing(self, x, y, fit):
            x_preprocessed, y_preprocessed = self._apply_preprocessing_defences(x, y, fit=fit)
            x_preprocessed = self._apply_preprocessing_normalization(x_preprocessed)
            return x_preprocessed, y_preprocessed

        def _apply_preprocessing_gradient(self, x, grads):
            grads = self._apply_preprocessing_normalization_gradient(grads)
            grads = self._apply_preprocessing_defences_gradient(x, grads)
            return grads

        def _apply_preprocessing_defences(self, x, y, fit=False):
            if self.defences is not None:
                for defence in self.defences:
                    if fit:
                        if defence.apply_fit:
                            x, y = defence(x, y)
                    else:
                        if defence.apply_predict:
                            x, y = defence(x, y)

            return x, y

        def _apply_preprocessing_defences_gradient(self, x, grads, fit=False):
            if self.defences is not None:
                for defence in self.defences[::-1]:
                    if fit:
                        if defence.apply_fit:
                            grads = defence.estimate_gradient(x, grads)
                    else:
                        if defence.apply_predict:
                            grads = defence.estimate_gradient(x, grads)

            return grads

        def _apply_preprocessing_normalization(self, x):
            sub, div = self.preprocessing
            sub = np.asarray(sub, dtype=x.dtype)
            div = np.asarray(div, dtype=x.dtype)

            res = x - sub
            res = res / div

            return res

        def _apply_preprocessing_normalization_gradient(self, grads):
            _, div = self.preprocessing
            div = np.asarray(div, dtype=grads.dtype)
            res = grads / div
            return res

        def __repr__(self):
            repr_ = "%s(channel_index=%r, clip_values=%r, defences=%r, preprocessing=%r)" \
                    % (self.__module__ + '.' + self.__class__.__name__,
                       self.channel_index, self.clip_values, self.defences, self.preprocessing)

            return repr_
    def generator_fit(x, y, batch_size=128):
            while True:
                indices = np.random.randint(x.shape[0], size=batch_size)
                yield x[indices], y[indices]
    class KerasClassifier(Classifier):
        def __init__(self, model, use_logits=False, channel_index=3, clip_values=None, defences=None, preprocessing=(0, 1),
                     input_layer=0, output_layer=0, custom_activation=False):
            super(KerasClassifier, self).__init__(clip_values=clip_values, channel_index=channel_index, defences=defences,
                                                  preprocessing=preprocessing)

            self._model = model
            self._input_layer = input_layer
            self._output_layer = output_layer

            self._initialize_params(model, use_logits, input_layer, output_layer, custom_activation)

        def _initialize_params(self, model, use_logits, input_layer, output_layer, custom_activation):
            if hasattr(model, 'inputs'):
                self._input_layer = input_layer
                self._input = model.inputs[input_layer]
            else:
                self._input = model.input
                self._input_layer = 0

            if hasattr(model, 'outputs'):
                self._output = model.outputs[output_layer]
                self._output_layer = output_layer
            else:
                self._output = model.output
                self._output_layer = 0

            _, self._nb_classes = k.int_shape(self._output)
            self._input_shape = k.int_shape(self._input)[1:]
            self._custom_activation = custom_activation
            logger.debug('Inferred %i classes and %s as input shape for Keras classifier.', self.nb_classes,
                         str(self.input_shape))

            # Get predictions and loss function
            label_ph = k.placeholder(shape=self._output.shape)
            if not hasattr(self._model, 'loss'):
                logger.warning('Keras model has no loss set. Trying to use `k.sparse_categorical_crossentropy`.')
                loss_function = k.sparse_categorical_crossentropy
            else:
                if isinstance(self._model.loss, six.string_types):
                    loss_function = getattr(k, self._model.loss)
                else:
                    loss_function = getattr(k, self._model.loss.__name__)

            self._use_logits = use_logits
            if not use_logits:
                if k.backend() == 'tensorflow':
                    if custom_activation:
                        preds = self._output
                        loss_ = loss_function(label_ph, preds, from_logits=False)
                    else:
                        # We get a list of tensors that comprise the final "layer" -> take the last element
                        preds = self._output.op.inputs[-1]
                        loss_ = loss_function(label_ph, preds, from_logits=True)
                else:
                    loss_ = loss_function(label_ph, self._output, from_logits=use_logits)

                    # Convert predictions to logits for consistency with the other cases
                    eps = 10e-8
                    preds = k.log(k.clip(self._output, eps, 1. - eps))
            else:
                preds = self._output
                loss_ = loss_function(label_ph, self._output, from_logits=use_logits)
            if preds == self._input:  # recent Tensorflow version does not allow a model with an output same as the input.
                preds = k.identity(preds)
            loss_grads = k.gradients(loss_, self._input)

            if k.backend() == 'tensorflow':
                loss_grads = loss_grads[0]
            elif k.backend() == 'cntk':
                raise NotImplementedError('Only TensorFlow and Theano support is provided for Keras.')

            # Set loss, grads and prediction functions
            self._preds_op = preds
            self._loss = loss_
            self._loss_grads = k.function([self._input, label_ph], [loss_grads])
            self._preds = k.function([self._input], [preds])

            # Set check for the shape of y for loss functions that do not take labels in one-hot encoding
            self._reduce_labels = (hasattr(self._loss.op, 'inputs') and
                                   not all(len(input_.shape) == len(self._loss.op.inputs[0].shape)
                                           for input_ in self._loss.op.inputs))

            # Get the internal layer
            self._layer_names = self._get_layers()

        def loss_gradient(self, x, y, **kwargs):
            # Apply preprocessing
            x_preprocessed, y_preprocessed = self._apply_preprocessing(x, y, fit=False)

            # Adjust the shape of y for loss functions that do not take labels in one-hot encoding
            if self._reduce_labels:
                y_preprocessed = np.argmax(y_preprocessed, axis=1)

            # Compute gradients
            grads = self._loss_grads([x_preprocessed, y_preprocessed])[0]
            grads = self._apply_preprocessing_gradient(x, grads)
            assert grads.shape == x_preprocessed.shape

            return grads

        def class_gradient(self, x, label=None, logits=False, **kwargs):
            # Check value of label for computing gradients
            if not (label is None or (isinstance(label, (int, np.integer)) and label in range(self.nb_classes))
                    or (isinstance(label, np.ndarray) and len(label.shape) == 1 and (label < self.nb_classes).all()
                        and label.shape[0] == x.shape[0])):
                raise ValueError('Label %s is out of range.' % str(label))

            self._init_class_grads(label=label, logits=logits)

            # Apply preprocessing
            x_preprocessed, _ = self._apply_preprocessing(x, y=None, fit=False)

            if label is None:
                # Compute the gradients w.r.t. all classes
                if logits:
                    grads = np.swapaxes(np.array(self._class_grads_logits([x_preprocessed])), 0, 1)
                else:
                    grads = np.swapaxes(np.array(self._class_grads([x_preprocessed])), 0, 1)

            elif isinstance(label, (int, np.integer)):
                # Compute the gradients only w.r.t. the provided label
                if logits:
                    grads = np.swapaxes(np.array(self._class_grads_logits_idx[label]([x_preprocessed])), 0, 1)
                else:
                    grads = np.swapaxes(np.array(self._class_grads_idx[label]([x_preprocessed])), 0, 1)

                assert grads.shape == (x_preprocessed.shape[0], 1) + self.input_shape

            else:
                # For each sample, compute the gradients w.r.t. the indicated target class (possibly distinct)
                unique_label = list(np.unique(label))
                if logits:
                    grads = np.array([self._class_grads_logits_idx[l]([x_preprocessed]) for l in unique_label])
                else:
                    grads = np.array([self._class_grads_idx[l]([x_preprocessed]) for l in unique_label])
                grads = np.swapaxes(np.squeeze(grads, axis=1), 0, 1)
                lst = [unique_label.index(i) for i in label]
                grads = np.expand_dims(grads[np.arange(len(grads)), lst], axis=1)

            grads = self._apply_preprocessing_gradient(x, grads)

            return grads

        def predict(self, x, logits=False, batch_size=128, **kwargs):
            from art import NUMPY_DTYPE

            # Apply defences
            x_preprocessed, _ = self._apply_preprocessing(x, y=None, fit=False)

            # Run predictions with batching
            preds = np.zeros((x_preprocessed.shape[0], self.nb_classes), dtype=NUMPY_DTYPE)
            for batch_index in range(int(np.ceil(x_preprocessed.shape[0] / float(batch_size)))):
                begin, end = batch_index * batch_size, min((batch_index + 1) * batch_size, x_preprocessed.shape[0])
                preds[begin:end] = self._preds([x_preprocessed[begin:end]])[0]

                if not logits and not self._custom_activation:
                    exp = np.exp(preds[begin:end] - np.max(preds[begin:end], axis=1, keepdims=True))
                    preds[begin:end] = exp / np.sum(exp, axis=1, keepdims=True)

            return preds

        def fit(self, x, y, batch_size=128, nb_epochs=20, **kwargs):
            # Apply preprocessing
            x_preprocessed, y_preprocessed = self._apply_preprocessing(x, y, fit=True)

            # Adjust the shape of y for loss functions that do not take labels in one-hot encoding
            if self._reduce_labels:
                y_preprocessed = np.argmax(y_preprocessed, axis=1)

            gen = generator_fit(x_preprocessed, y_preprocessed, batch_size)
            self._model.fit_generator(gen, steps_per_epoch=x_preprocessed.shape[0] / batch_size, epochs=nb_epochs, **kwargs)

        def fit_generator(self, generator, nb_epochs=20, **kwargs):
            from art.data_generators import KerasDataGenerator

            # Try to use the generator as a Keras native generator, otherwise use it through the `DataGenerator` interface
            if isinstance(generator, KerasDataGenerator) and not hasattr(self, 'defences'):
                try:
                    self._model.fit_generator(generator.generator, epochs=nb_epochs, **kwargs)
                except ValueError:
                    logger.info('Unable to use data generator as Keras generator. Now treating as framework-independent.')
                    super(KerasClassifier, self).fit_generator(generator, nb_epochs=nb_epochs, **kwargs)
            else:
                super(KerasClassifier, self).fit_generator(generator, nb_epochs=nb_epochs, **kwargs)

        @property
        def layer_names(self):
            return self._layer_names

        def get_activations(self, x, layer, batch_size=128):
            import keras.backend as k
            from art import NUMPY_DTYPE

            if isinstance(layer, six.string_types):
                if layer not in self._layer_names:
                    raise ValueError('Layer name %s is not part of the graph.' % layer)
                layer_name = layer
            elif isinstance(layer, int):
                if layer < 0 or layer >= len(self._layer_names):
                    raise ValueError('Layer index %d is outside of range (0 to %d included).'
                                     % (layer, len(self._layer_names) - 1))
                layer_name = self._layer_names[layer]
            else:
                raise TypeError('Layer must be of type `str` or `int`.')

            layer_output = self._model.get_layer(layer_name).output
            output_func = k.function([self._input], [layer_output])

            if x.shape == self.input_shape:
                x_expanded = np.expand_dims(x, 0)
            else:
                x_expanded = x

            # Apply preprocessing
            x_preprocessed, _ = self._apply_preprocessing(x=x_expanded, y=None, fit=False)

            assert len(x_preprocessed.shape) == 4

            # Determine shape of expected output and prepare array
            output_shape = output_func([x_preprocessed[0][None, ...]])[0].shape
            activations = np.zeros((x_preprocessed.shape[0],) + output_shape[1:], dtype=NUMPY_DTYPE)

            # Get activations with batching
            for batch_index in range(int(np.ceil(x_preprocessed.shape[0] / float(batch_size)))):
                begin, end = batch_index * batch_size, min((batch_index + 1) * batch_size, x_preprocessed.shape[0])
                activations[begin:end] = output_func([x_preprocessed[begin:end]])[0]

            return activations

        def _init_class_grads(self, label=None, logits=False):
            import keras.backend as k

            if len(self._output.shape) == 2:
                nb_outputs = self._output.shape[1]
            else:
                raise ValueError('Unexpected output shape for classification in Keras model.')

            if label is None:
                logger.debug('Computing class gradients for all %i classes.', self.nb_classes)
                if logits:
                    if not hasattr(self, '_class_grads_logits'):
                        class_grads_logits = [k.gradients(self._preds_op[:, i], self._input)[0]
                                              for i in range(nb_outputs)]
                        self._class_grads_logits = k.function([self._input], class_grads_logits)
                else:
                    if not hasattr(self, '_class_grads'):
                        class_grads = [k.gradients(k.softmax(self._preds_op)[:, i], self._input)[0]
                                       for i in range(nb_outputs)]
                        self._class_grads = k.function([self._input], class_grads)

            else:
                if isinstance(label, int):
                    unique_labels = [label]
                    logger.debug('Computing class gradients for class %i.', label)
                else:
                    unique_labels = np.unique(label)
                    logger.debug('Computing class gradients for classes %s.', str(unique_labels))

                if logits:
                    if not hasattr(self, '_class_grads_logits_idx'):
                        self._class_grads_logits_idx = [None for _ in range(nb_outputs)]

                    for current_label in unique_labels:
                        if self._class_grads_logits_idx[current_label] is None:
                            class_grads_logits = [k.gradients(self._preds_op[:, current_label], self._input)[0]]
                            self._class_grads_logits_idx[current_label] = k.function([self._input], class_grads_logits)
                else:
                    if not hasattr(self, '_class_grads_idx'):
                        self._class_grads_idx = [None for _ in range(nb_outputs)]

                    for current_label in unique_labels:
                        if self._class_grads_idx[current_label] is None:
                            class_grads = [k.gradients(k.softmax(self._preds_op)[:, current_label], self._input)[0]]
                            self._class_grads_idx[current_label] = k.function([self._input], class_grads)

        def _get_layers(self):
            from keras.engine.topology import InputLayer
            layer_names = [layer.name for layer in self._model.layers[:-1] if not isinstance(layer, InputLayer)]
            logger.info('Inferred %i hidden layers on Keras classifier.', len(layer_names))

            return layer_names

        def set_learning_phase(self, train):
            import keras.backend as k

            if isinstance(train, bool):
                self._learning_phase = train
                k.set_learning_phase(int(train))

        def save(self, filename, path=None):
            import os

            if path is None:
                from art import DATA_PATH
                full_path = os.path.join(DATA_PATH, filename)
            else:
                full_path = os.path.join(path, filename)
            folder = os.path.split(full_path)[0]
            if not os.path.exists(folder):
                os.makedirs(folder)

            self._model.save(str(full_path))
            logger.info('Model saved in path: %s.', full_path)

        def __getstate__(self):
            import time

            state = self.__dict__.copy()

            # Remove the unpicklable entries
            del state['_model']
            del state['_input']
            del state['_output']
            del state['_preds_op']
            del state['_loss']
            del state['_loss_grads']
            del state['_preds']
            del state['_layer_names']

            model_name = str(time.time()) + '.h5'
            state['model_name'] = model_name
            self.save(model_name)
            return state

        def __setstate__(self, state):
            self.__dict__.update(state)

            # Load and update all functionality related to Keras
            import os
            from art import DATA_PATH
            from keras.models import load_model

            full_path = os.path.join(DATA_PATH, state['model_name'])
            model = load_model(str(full_path))

            self._model = model
            self._initialize_params(model, state['_use_logits'], state['_input_layer'], state['_output_layer'],
                                    state['_custom_activation'])

        def __repr__(self):
            repr_ = "%s(model=%r, use_logits=%r, channel_index=%r, clip_values=%r, defences=%r, preprocessing=%r, " \
                    "input_layer=%r, output_layer=%r, custom_activation=%r)" \
                    % (self.__module__ + '.' + self.__class__.__name__,
                       self._model, self._use_logits, self.channel_index, self.clip_values, self.defences,
                       self.preprocessing, self._input_layer, self._output_layer, self._custom_activation)

            return repr_
    class Attack(ABC):
        attack_params = ['classifier']

        def __init__(self, classifier):
            self.classifier = classifier

        def generate(self, x, y=None, **kwargs):
            raise NotImplementedError

        def set_params(self, **kwargs):
            for key, value in kwargs.items():
                if key in self.attack_params:
                    setattr(self, key, value)
            return True
    class CarliniL2Method(Attack):
        attack_params = Attack.attack_params + ['confidence', 'targeted', 'learning_rate', 'max_iter',
                                                'binary_search_steps', 'initial_const', 'max_halving', 'max_doubling',
                                                'batch_size']

        def __init__(self, classifier, confidence=0.0, targeted=False, learning_rate=0.01, binary_search_steps=10,
                     max_iter=10, initial_const=0.01, max_halving=5, max_doubling=5, batch_size=1):
            super(CarliniL2Method, self).__init__(classifier)

            kwargs = {'confidence': confidence,
                      'targeted': targeted,
                      'learning_rate': learning_rate,
                      'binary_search_steps': binary_search_steps,
                      'max_iter': max_iter,
                      'initial_const': initial_const,
                      'max_halving': max_halving,
                      'max_doubling': max_doubling,
                      'batch_size': batch_size
                      }
            assert self.set_params(**kwargs)

            # There are internal hyperparameters:
            # Abort binary search for c if it exceeds this threshold (suggested in Carlini and Wagner (2016)):
            self._c_upper_bound = 10e10

            # Smooth arguments of arctanh by multiplying with this constant to avoid division by zero.
            # It appears this is what Carlini and Wagner (2016) are alluding to in their footnote 8. However, it is not
            # clear how their proposed trick ("instead of scaling by 1/2 we scale by 1/2 + eps") works in detail.
            self._tanh_smoother = 0.999999

        def _loss(self, x, x_adv, target, c_weight):
            l2dist = np.sum(np.square(x - x_adv).reshape(x.shape[0], -1), axis=1)
            z_predicted = self.classifier.predict(np.array(x_adv, dtype=NUMPY_DTYPE), logits=True,
                                                  batch_size=self.batch_size)
            z_target = np.sum(z_predicted * target, axis=1)
            z_other = np.max(z_predicted * (1 - target) + (np.min(z_predicted, axis=1) - 1)[:, np.newaxis] * target, axis=1)

            # The following differs from the exact definition given in Carlini and Wagner (2016). There (page 9, left
            # column, last equation), the maximum is taken over Z_other - Z_target (or Z_target - Z_other respectively)
            # and -confidence. However, it doesn't seem that that would have the desired effect (loss term is <= 0 if and
            # only if the difference between the logit of the target and any other class differs by at least confidence).
            # Hence the rearrangement here.

            if self.targeted:
                # if targeted, optimize for making the target class most likely
                loss = np.maximum(z_other - z_target + self.confidence, np.zeros(x.shape[0]))
            else:
                # if untargeted, optimize for making any other class most likely
                loss = np.maximum(z_target - z_other + self.confidence, np.zeros(x.shape[0]))

            return z_predicted, l2dist, c_weight * loss + l2dist

        def _loss_gradient(self, z_logits, target, x, x_adv, x_adv_tanh, c_weight, clip_min, clip_max):
            if self.targeted:
                i_sub = np.argmax(target, axis=1)
                i_add = np.argmax(z_logits * (1 - target) + (np.min(z_logits, axis=1) - 1)[:, np.newaxis] * target, axis=1)
            else:
                i_add = np.argmax(target, axis=1)
                i_sub = np.argmax(z_logits * (1 - target) + (np.min(z_logits, axis=1) - 1)[:, np.newaxis] * target, axis=1)

            loss_gradient = self.classifier.class_gradient(x_adv, label=i_add, logits=True)
            loss_gradient -= self.classifier.class_gradient(x_adv, label=i_sub, logits=True)
            loss_gradient = loss_gradient.reshape(x.shape)

            c_mult = c_weight
            for _ in range(len(x.shape) - 1):
                c_mult = c_mult[:, np.newaxis]

            loss_gradient *= c_mult
            loss_gradient += 2 * (x_adv - x)
            loss_gradient *= (clip_max - clip_min)
            loss_gradient *= (1 - np.square(np.tanh(x_adv_tanh))) / (2 * self._tanh_smoother)

            return loss_gradient

        def generate(self, x, y=None, **kwargs):
            x_adv = x.astype(NUMPY_DTYPE)
            if hasattr(self.classifier, 'clip_values') and self.classifier.clip_values is not None:
                clip_min, clip_max = self.classifier.clip_values
            else:
                clip_min, clip_max = np.amin(x), np.amax(x)

            # Assert that, if attack is targeted, y_val is provided:
            if self.targeted and y is None:
                raise ValueError('Target labels `y` need to be provided for a targeted attack.')

            # No labels provided, use model prediction as correct class
            if y is None:
                y = get_labels_np_array(self.classifier.predict(x, logits=False, batch_size=self.batch_size))

            # Compute perturbation with implicit batching
            nb_batches = int(np.ceil(x_adv.shape[0] / float(self.batch_size)))
            for batch_id in range(nb_batches):
                logger.debug('Processing batch %i out of %i', batch_id, nb_batches)

                batch_index_1, batch_index_2 = batch_id * self.batch_size, (batch_id + 1) * self.batch_size
                x_batch = x_adv[batch_index_1:batch_index_2]
                y_batch = y[batch_index_1:batch_index_2]

                # The optimization is performed in tanh space to keep the adversarial images bounded in correct range
                x_batch_tanh = original_to_tanh(x_batch, clip_min, clip_max, self._tanh_smoother)

                # Initialize binary search:
                c_current = self.initial_const * np.ones(x_batch.shape[0])
                c_lower_bound = np.zeros(x_batch.shape[0])
                c_double = (np.ones(x_batch.shape[0]) > 0)

                # Initialize placeholders for best l2 distance and attack found so far
                best_l2dist = np.inf * np.ones(x_batch.shape[0])
                best_x_adv_batch = x_batch.copy()

                for bss in range(self.binary_search_steps):
                    logger.debug('Binary search step %i out of %i (c_mean==%f)', bss, self.binary_search_steps,
                                 np.mean(c_current))
                    nb_active = int(np.sum(c_current < self._c_upper_bound))
                    logger.debug('Number of samples with c_current < _c_upper_bound: %i out of %i', nb_active,
                                 x_batch.shape[0])
                    if nb_active == 0:
                        break
                    learning_rate = self.learning_rate * np.ones(x_batch.shape[0])

                    # Initialize perturbation in tanh space:
                    x_adv_batch = x_batch.copy()
                    x_adv_batch_tanh = x_batch_tanh.copy()

                    z_logits, l2dist, loss = self._loss(x_batch, x_adv_batch, y_batch, c_current)
                    attack_success = (loss - l2dist <= 0)
                    overall_attack_success = attack_success

                    for i_iter in range(self.max_iter):
                        logger.debug('Iteration step %i out of %i', i_iter, self.max_iter)
                        logger.debug('Average Loss: %f', np.mean(loss))
                        logger.debug('Average L2Dist: %f', np.mean(l2dist))
                        logger.debug('Average Margin Loss: %f', np.mean(loss - l2dist))
                        logger.debug('Current number of succeeded attacks: %i out of %i', int(np.sum(attack_success)),
                                     len(attack_success))

                        improved_adv = attack_success & (l2dist < best_l2dist)
                        logger.debug('Number of improved L2 distances: %i', int(np.sum(improved_adv)))
                        if np.sum(improved_adv) > 0:
                            best_l2dist[improved_adv] = l2dist[improved_adv]
                            best_x_adv_batch[improved_adv] = x_adv_batch[improved_adv]

                        active = (c_current < self._c_upper_bound) & (learning_rate > 0)
                        nb_active = int(np.sum(active))
                        logger.debug(
                            'Number of samples with c_current < _c_upper_bound and learning_rate > 0: %i out of %i',
                            nb_active, x_batch.shape[0])
                        if nb_active == 0:
                            break

                        # compute gradient:
                        logger.debug('Compute loss gradient')
                        perturbation_tanh = -self._loss_gradient(z_logits[active], y_batch[active], x_batch[active],
                                                                 x_adv_batch[active], x_adv_batch_tanh[active],
                                                                 c_current[active], clip_min, clip_max)

                        # perform line search to optimize perturbation
                        # first, halve the learning rate until perturbation actually decreases the loss:
                        prev_loss = loss.copy()
                        best_loss = loss.copy()
                        best_lr = np.zeros(x_batch.shape[0])
                        halving = np.zeros(x_batch.shape[0])

                        for i_halve in range(self.max_halving):
                            logger.debug('Perform halving iteration %i out of %i', i_halve, self.max_halving)
                            do_halving = (loss[active] >= prev_loss[active])
                            logger.debug('Halving to be performed on %i samples', int(np.sum(do_halving)))
                            if np.sum(do_halving) == 0:
                                break
                            active_and_do_halving = active.copy()
                            active_and_do_halving[active] = do_halving

                            lr_mult = learning_rate[active_and_do_halving]
                            for _ in range(len(x.shape) - 1):
                                lr_mult = lr_mult[:, np.newaxis]

                            new_x_adv_batch_tanh = x_adv_batch_tanh[active_and_do_halving] + lr_mult * perturbation_tanh[
                                do_halving]
                            new_x_adv_batch = tanh_to_original(new_x_adv_batch_tanh, clip_min, clip_max,
                                                               self._tanh_smoother)
                            _, l2dist[active_and_do_halving], loss[active_and_do_halving] = self._loss(
                                x_batch[active_and_do_halving], new_x_adv_batch, y_batch[active_and_do_halving],
                                c_current[active_and_do_halving])

                            logger.debug('New Average Loss: %f', np.mean(loss))
                            logger.debug('New Average L2Dist: %f', np.mean(l2dist))
                            logger.debug('New Average Margin Loss: %f', np.mean(loss - l2dist))

                            best_lr[loss < best_loss] = learning_rate[loss < best_loss]
                            best_loss[loss < best_loss] = loss[loss < best_loss]
                            learning_rate[active_and_do_halving] /= 2
                            halving[active_and_do_halving] += 1
                        learning_rate[active] *= 2

                        # if no halving was actually required, double the learning rate as long as this
                        # decreases the loss:
                        for i_double in range(self.max_doubling):
                            logger.debug('Perform doubling iteration %i out of %i', i_double, self.max_doubling)
                            do_doubling = (halving[active] == 1) & (loss[active] <= best_loss[active])
                            logger.debug('Doubling to be performed on %i samples', int(np.sum(do_doubling)))
                            if np.sum(do_doubling) == 0:
                                break
                            active_and_do_doubling = active.copy()
                            active_and_do_doubling[active] = do_doubling
                            learning_rate[active_and_do_doubling] *= 2

                            lr_mult = learning_rate[active_and_do_doubling]
                            for _ in range(len(x.shape) - 1):
                                lr_mult = lr_mult[:, np.newaxis]

                            new_x_adv_batch_tanh = x_adv_batch_tanh[active_and_do_doubling] + lr_mult * perturbation_tanh[
                                do_doubling]
                            new_x_adv_batch = tanh_to_original(new_x_adv_batch_tanh, clip_min, clip_max,
                                                               self._tanh_smoother)
                            _, l2dist[active_and_do_doubling], loss[active_and_do_doubling] = self._loss(
                                x_batch[active_and_do_doubling], new_x_adv_batch, y_batch[active_and_do_doubling],
                                c_current[active_and_do_doubling])
                            logger.debug('New Average Loss: %f', np.mean(loss))
                            logger.debug('New Average L2Dist: %f', np.mean(l2dist))
                            logger.debug('New Average Margin Loss: %f', np.mean(loss - l2dist))
                            best_lr[loss < best_loss] = learning_rate[loss < best_loss]
                            best_loss[loss < best_loss] = loss[loss < best_loss]

                        learning_rate[halving == 1] /= 2

                        update_adv = (best_lr[active] > 0)
                        logger.debug('Number of adversarial samples to be finally updated: %i', int(np.sum(update_adv)))

                        if np.sum(update_adv) > 0:
                            active_and_update_adv = active.copy()
                            active_and_update_adv[active] = update_adv
                            best_lr_mult = best_lr[active_and_update_adv]
                            for _ in range(len(x.shape) - 1):
                                best_lr_mult = best_lr_mult[:, np.newaxis]
                            x_adv_batch_tanh[active_and_update_adv] = x_adv_batch_tanh[
                                active_and_update_adv] + best_lr_mult * perturbation_tanh[update_adv]
                            x_adv_batch[active_and_update_adv] = tanh_to_original(x_adv_batch_tanh[active_and_update_adv],
                                                                                  clip_min, clip_max, self._tanh_smoother)
                            z_logits[active_and_update_adv], l2dist[active_and_update_adv], loss[active_and_update_adv] = \
                                self._loss(x_batch[active_and_update_adv], x_adv_batch[active_and_update_adv],
                                           y_batch[active_and_update_adv], c_current[active_and_update_adv])
                            attack_success = (loss - l2dist <= 0)
                            overall_attack_success = overall_attack_success | attack_success

                    # Update depending on attack success:
                    improved_adv = attack_success & (l2dist < best_l2dist)
                    logger.debug('Number of improved L2 distances: %i', int(np.sum(improved_adv)))

                    if np.sum(improved_adv) > 0:
                        best_l2dist[improved_adv] = l2dist[improved_adv]
                        best_x_adv_batch[improved_adv] = x_adv_batch[improved_adv]

                    c_double[overall_attack_success] = False
                    c_current[overall_attack_success] = (c_lower_bound + c_current)[overall_attack_success] / 2

                    c_old = c_current
                    c_current[~overall_attack_success & c_double] *= 2
                    c_current[~overall_attack_success & ~c_double] += (c_current - c_lower_bound)[
                        ~overall_attack_success & ~c_double] / 2
                    c_lower_bound[~overall_attack_success] = c_old[~overall_attack_success]

                x_adv[batch_index_1:batch_index_2] = best_x_adv_batch

            logger.info('Success rate of C&W L_2 attack: %.2f%%',
                        100 * compute_success(self.classifier, x, y, x_adv, self.targeted, batch_size=self.batch_size))

            return x_adv

        def set_params(self, **kwargs):
            # Save attack-specific parameters
            super(CarliniL2Method, self).set_params(**kwargs)

            if not isinstance(self.binary_search_steps, (int, np.int)) or self.binary_search_steps < 0:
                raise ValueError("The number of binary search steps must be a non-negative integer.")

            if not isinstance(self.max_iter, (int, np.int)) or self.max_iter < 0:
                raise ValueError("The number of iterations must be a non-negative integer.")

            if not isinstance(self.max_halving, (int, np.int)) or self.max_halving < 1:
                raise ValueError("The number of halving steps must be an integer greater than zero.")

            if not isinstance(self.max_doubling, (int, np.int)) or self.max_doubling < 1:
                raise ValueError("The number of doubling steps must be an integer greater than zero.")

            if not isinstance(self.batch_size, (int, np.int)) or self.batch_size < 1:
                raise ValueError("The batch size must be an integer greater than zero.")

            return True


# 数据集加载与预处理
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.reshape(-1, 1, 28, 28)/255
x_test = x_test.reshape(-1, 1, 28, 28)/255
y_train = np_utils.to_categorical(y_train, num_classes=10)
y_test = np_utils.to_categorical(y_test, num_classes=10)
k.set_learning_phase(1)

# 创建模型
model = Sequential()
# 第一个卷积，激活，池化
model.add(Convolution2D(
    batch_input_shape=(None, 1, 28, 28),
    filters=32,         # 滤波器数量，即下一层层数
    kernel_size=5,
    strides=1,
    padding='same',
    data_format='channels_first',
    activation='relu'
))
model.add(MaxPooling2D(
    pool_size=2,
    strides=2,
    padding='same',
    data_format='channels_first'
))
# 第二个卷积，激活，池化
model.add(Convolution2D(
    filters=64,
    kernel_size=5,
    strides=1,
    padding='same',
    data_format='channels_first',
    activation='relu'
))
model.add(MaxPooling2D(
    pool_size=2,
    strides=2,
    padding='same',
    data_format='channels_first'
))
# 拉直
model.add(Flatten())
# 全连接层
model.add(Dense(1024, activation='relu'))
model.add(Dense(10, activation='softmax'))
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
classifier = KerasClassifier(model=model)
classifier.fit(x_train, y_train, nb_epochs=5, batch_size=128)

# 定几个常数
K = 0  # f内的损失项常数 k
LEARNING_RATE = 0.0001  # 使用C&W方法优化的学习率
BS = 20  # c 的搜索次数
MAX_ITER = 20  # 最大迭代次数
INITIAL_CONST = 0.001  # c的初始值

# 单张图片展示
xx = x_train[0].reshape([1, 1, 28, 28])
adv_crafter = CarliniL2Method(classifier,K,False,LEARNING_RATE,BS,MAX_ITER,INITIAL_CONST)
x_test_adv = adv_crafter.generate(x=xx)
plt.imshow(xx.reshape([28,28]))
plt.show()
plt.imshow(x_test_adv.reshape([28, 28]))
plt.show()
print(np.argmax(classifier.predict(xx)), end=' ')
print(np.argmax(classifier.predict(x_test_adv)))

# 计算平均l2 norm
su = 0
for i in range(100):
    xx = x_test[i].reshape([1, 1, 28, 28])
    adv_crafter = CarliniL2Method(classifier,K,False,LEARNING_RATE,BS,MAX_ITER,INITIAL_CONST)
    x_test_adv = adv_crafter.generate(x=xx)
    su += np.linalg.norm(x_test_adv-xx)
print('average l2 norm:', su/100)
