from .affine import Affine
from ... import describe
from ... import check
from ...describe import Dimension, Synapses, Biases
from ...check import has_shape


class ReLu(Affine):
    @check.arg(1, has_shape(('nB', 'nI')))
    def predict(self, input__BI):
        output__BO = Affine.predict(self, input__BI)
        output__BO = output__BO.copy()
        output__BO = self.ops.relu(output__BO, inplace=True)
        return output__BO

    @check.arg(1, has_shape(('nB', 'nI')))
    def begin_update(self, input__BI, drop=0.0):
        output__BO, finish_affine = Affine.begin_update(self, input__BI, drop=0.)
        output_copy = output__BO.copy()
        output_copy = self.ops.relu(output_copy, inplace=True)
        @check.arg(0, has_shape(('nB', 'nO')))
        def finish_update(gradient, sgd=None):
            gradient = gradient.copy()
            gradient = self.ops.backprop_relu(gradient, output_copy, inplace=True)
            return finish_affine(gradient, sgd)
        output__BO[:] = output_copy
        output__BO, bp_dropout = self.ops.dropout(output__BO, drop, inplace=True)
        return output__BO, bp_dropout(finish_update)
