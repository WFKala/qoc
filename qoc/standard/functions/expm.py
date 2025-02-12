"""
expm.py - a module for all things e^M
"""

from autograd.extend import (defvjp as autograd_defvjp,
                             primitive as autograd_primitive)
import autograd.numpy as anp
import numpy as np
import scipy.linalg as la
from numba import jit

@autograd_primitive
def expm(matrix):
    """
    Compute the matrix exponential of a matrix.
    Args:
    matrix :: numpy.ndarray - the matrix to exponentiate
    operation_policy :: qoc.OperationPolicy - what data type is
        used to perform the operation and with which method
    Returns:
    exp_matrix :: numpy.ndarray - the exponentiated matrix
    """
    exp_matrix = la.expm(matrix)

    return exp_matrix


@jit(nopython=True, parallel=True)
def _expm_vjp_(dfinal_dexpm, exp_matrix, matrix_size):
    dfinal_dmatrix = np.zeros((matrix_size, matrix_size), dtype=np.complex128)

    # Compute a first order approximation of the frechet derivative of the matrix
    # exponential in every unit direction Eij.
    for i in range(matrix_size):
        for j in range(matrix_size):
            dexpm_dmij_rowi = exp_matrix[j,:]
            dfinal_dmatrix[i, j] = np.sum(np.multiply(dfinal_dexpm[i, :], dexpm_dmij_rowi))
        #ENDFOR
    #ENDFOR
    return dfinal_dmatrix


def _expm_vjp(exp_matrix, matrix):
    """
    Construct the left-multiplying vector jacobian product function
    for the matrix exponential.

    Intuition:
    `dfinal_dexpm` is the jacobian of `final` with respect to each element `expmij`
    of `exp_matrix`. `final` is the output of the first function in the
    backward differentiation series. It is also the output of the last
    function evaluated in the chain of functions that is being differentiated,
    i.e. the final cost function. The goal of `vjp_function` is to take
    `dfinal_dexpm` and yield `dfinal_dmatrix` which is the jacobian of
    `final` with respect to each element `mij` of `matrix`.
    To compute the frechet derivative of the matrix exponential with respect
    to each element `mij`, we use the approximation that
    dexpm_dmij = np.matmul(Eij, exp_matrix). Since Eij has a specific
    structure we don't need to do the full matrix multiplication and instead
    use some indexing tricks.

    Args:
    exp_matrix :: numpy.ndarray - the matrix exponential of matrix
    matrix :: numpy.ndarray - the matrix that was exponentiated
    operation_policy :: qoc.OperationPolicy - what data type is
        used to perform the operation and with which method

    Returns:
    vjp_function :: numpy.ndarray -> numpy.ndarray - the function that takes
        the jacobian of the final function with respect to `exp_matrix`
        to the jacobian of the final function with respect to `matrix`
    """
    matrix_size = matrix.shape[0]
    return lambda dfinal_dexpm: _expm_vjp_(dfinal_dexpm, exp_matrix, matrix_size)


autograd_defvjp(expm, _expm_vjp)
