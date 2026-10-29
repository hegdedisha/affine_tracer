from __future__ import annotations

from egglog import *
from collections.abc import Iterable
from inspect import getmembers, isfunction
from typing import *
import numpy as np
import scipy
from icecream import ic

if TYPE_CHECKING: from .tracer import polytree

class Matrix(Expr):

    def __init__(self, rows: i64Like, cols: i64Like) -> None:
        pass

    @property
    def row(self) -> i64Like: ...

    @property
    def col(self) -> i64Like: ...

    @classmethod
    def identity(cls, Dim: i64Like) -> Matrix:
        cls.Dim = Dim
        """
        Create an identity matrix of the given dimension.
        """

    @classmethod
    def named(cls, name: StringLike, row: i64Like, col: i64Like) -> Matrix:
        cls.name = name
        # self.row = row
        # self.col = col
        """
        Create a named matrix.
        """

    @classmethod
    def sym(cls, name: StringLike, row: i64Like, col: i64Like) -> Matrix:
        cls.name = name
        # self.row = row
        # self.col = col
        """
        Create a named matrix.
        """

    @classmethod
    def zero(cls, row: i64Like, col: i64Like) -> Matrix:
        # cls.Dim = Dim
        """
        Create an zero matrix
        """

    @method()
    def __matmul__(self, other: Matrix) -> Matrix:
        """
        Matrix multiplication.
        """

    @method()
    @property
    def T(self) -> Matrix:
        """
        Matrix multiplication.
        """

    @method()
    def inverse(self) -> Matrix:
        """
        Matrix Inversion
        """

    @method()
    def __radd__(self, other: Matrix) -> Matrix:
        """
        Matrix right addition
        """

    @method()
    def __add__(self, other: Matrix) -> Matrix:
        """
        Matrix addition
        """

    # scalar is not defined
    # @method(cost = 10)
    # def __mul__(self, other: Num) -> Matrix:
    #     """
    #     Scalar multiplication
    #     """
    
    @method()
    def __rmatmul__(self, other: Matrix) -> Matrix:
        """
        Matrix right multiplication.
        """

    @method()
    def __rsub__(self, other: Matrix) -> Matrix:
        """
        Matrix right subtraction
        """

    @method()
    def __sub__(self, other: Matrix) -> Matrix:
        """
        Matrix subtraction
        """

    @method()
    def __neg__(self) -> Matrix:
        """
        Negative of a Matrix=
        """

    @method(cost = 1)
    def ltrisolve(self) -> Matrix:
        """
        Lower Triangular Matrix Inversion
        """
    # @method()
    # def name(self)

    @method()
    def A_inverse(self) -> Matrix:
        """
        Matrix Inversion
        """
    pass


#different rulesets - with different comibinations of rules to be used for different purposes

optimisations = ruleset()
@optimisations.register
def _id_ops(A : Matrix, B: Matrix, d: i64Like) -> Iterable[RewriteOrRule]:
    yield rewrite(Matrix.identity(d) @ A).to(A)
    yield rewrite(A @ Matrix.identity(d)).to(A)
    yield rewrite(A @ Matrix.identity(d) @ B).to(A @ B)
    yield rewrite((Matrix.identity(d).T)).to(Matrix.identity(d))
    yield rewrite((Matrix.identity(d)).inverse()).to(Matrix.identity(d))
    # yield rewrite((A + Matrix.identity(d)) @ A.inverse()).to(Matrix.identity(d) + A.inverse())

@optimisations.register
def _inv_ops(A: Matrix, B: Matrix, d: i64Like, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    yield rewrite(A @ A.inverse() @ B).to(B)
    yield rewrite(B @ A @ A.inverse()).to(B)
    yield rewrite(A @ (A.inverse() @ B)).to(B)
    yield rewrite(A.inverse() @ A @ B).to(B)
    yield rewrite(B @ A.inverse() @ A).to(B)
    yield rewrite(A.inverse() @ (A @ B)).to(B)
    yield rewrite((A @ B).inverse()).to(B.inverse() @ A.inverse())
    yield rewrite(A.inverse().inverse()).to(A)

@optimisations.register
def _inv_ops2(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)
    yield rewrite(A.inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.inverse()).to(Matrix.identity(r))
    yield rewrite(B.inverse() @ B).to(Matrix.identity(r))
    yield rewrite(B @ B.inverse()).to(Matrix.identity(r))
    yield rewrite(C.inverse()).to(C)
    yield rewrite(C.inverse() @ C).to(C)
    yield rewrite(C @ C.inverse()).to(C)

@optimisations.register
def _Ainv_ops(A: Matrix, B: Matrix, d: i64Like, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    yield rewrite(A @ A.A_inverse() @ B).to(B)
    yield rewrite(B @ A @ A.A_inverse()).to(B)
    yield rewrite(A @ (A.A_inverse() @ B)).to(B)
    yield rewrite(A.A_inverse() @ A @ B).to(B)
    yield rewrite(B @ A.A_inverse() @ A).to(B)
    yield rewrite(A.A_inverse() @ (A @ B)).to(B)
    yield rewrite((A @ B).A_inverse()).to(B.A_inverse() @ A.A_inverse())
    yield rewrite(A.A_inverse().A_inverse()).to(A)

@optimisations.register
def _Ainv_ops2(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)
    yield rewrite(A.A_inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.A_inverse()).to(Matrix.identity(r))
    yield rewrite(B.A_inverse() @ B).to(Matrix.identity(r))
    yield rewrite(B @ B.A_inverse()).to(Matrix.identity(r))
    yield rewrite(C.A_inverse().A_inverse()).to(C)
    yield rewrite(C.A_inverse() @ C).to(C)
    yield rewrite(C @ C.A_inverse()).to(C)

@optimisations.register
def _neg2(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]: 
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)   
    yield rewrite(A - A).to(Matrix.zero(r, c))
    yield rewrite(A + (-A)).to(Matrix.zero(r, c))
    yield rewrite(B - B).to(Matrix.zero(r, c))
    yield rewrite(B + (-B)).to(Matrix.zero(r, c))
    yield rewrite(C - C).to(Matrix.zero(r, r))
    yield rewrite(C + (-C)).to(Matrix.zero(r, r))
    yield rewrite((A.inverse() - A.inverse())).to(Matrix.zero(r, c))
    yield rewrite((B.inverse() - B.inverse())).to(Matrix.zero(r, c))
    yield rewrite((A.A_inverse() - A.A_inverse())).to(Matrix.zero(r, c))
    yield rewrite((B.A_inverse() - B.A_inverse())).to(Matrix.zero(r, c))

@optimisations.register
def _neg(A: Matrix, B: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A - B).to(A + (-B))
    yield rewrite(A - (-B)).to(A + B)
    yield rewrite(A + (-B)).to(A - B)
    yield rewrite(A @ (-B)).to(- (A @ B))
    yield rewrite((-A) @ (B)).to(- (A @ B))

@optimisations.register
def _add_assoc(A: Matrix, B: Matrix, C: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A + B).to(B + A)
    yield rewrite((A + B) + C).to(A + (B + C))

@optimisations.register
def _mul_assoc(A : Matrix, B: Matrix, C: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite((A @ B) @ C).to(A @ (B @ C))
    # yield rewrite(A @ (B @ C)).to(A @(B @ C))

@optimisations.register
def _mul_distrib(A: Matrix, B: Matrix, C: Matrix, D: Matrix) -> Iterable[RewriteOrRule]:
    yield birewrite((A + B) @ C).to((A @ C) + (B @ C))
    yield birewrite(A @ (B + C)).to((A @ B) + (A @ C))
    yield birewrite((A - B) @ C).to((A @ C) - (B @ C))
    yield birewrite(A @ (B - C)).to((A @ B) - (A @ C))

@optimisations.register
def _add_comm(A: Matrix, B: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A + B).to(B + A)

@optimisations.register
def __transpose(A: Matrix, B: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A.T.T).to(A)
    yield rewrite((A @ B).T).to(B.T @ A.T)
    yield rewrite((A.T).inverse()).to((A.inverse()).T)
    yield rewrite((A.T).A_inverse()).to((A.A_inverse()).T)
    yield rewrite((A + B).T).to(A.T + B.T)
    yield rewrite((A - B).T).to(A.T - B.T)

@optimisations.register
def __sym(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.sym(name, row = r, col = c)
    yield rewrite(A.T).to(A)
    yield rewrite(A.inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.inverse()).to(Matrix.identity(r))
    yield rewrite(A.inverse().T).to(A.inverse())
    yield rewrite(A.A_inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.A_inverse()).to(Matrix.identity(r))
    yield rewrite(A.A_inverse().T).to(A.A_inverse())

@optimisations.register
def __zero(name: StringLike, r: i64Like, c: i64Like, m: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)

    yield rewrite(Matrix.zero(r, c).T).to(Matrix.zero(c, r))
    # yield rewrite(Matrix.zero().inverse()).to(Matrix.zero())


    yield rewrite(Matrix.zero(m, r) @ A).to(Matrix.zero(m, c))
    yield rewrite(A @ Matrix.zero(c, m)).to(Matrix.zero(r, m))
    yield rewrite(Matrix.zero(m, c) @ A.T).to(Matrix.zero(m, r))
    yield rewrite(A.T @ Matrix.zero(r, m)).to(Matrix.zero(c, m))
    # yield rewrite(A @ Matrix.zero(d) @ B).to(Matrix.zero(d))
    yield rewrite(Matrix.zero(r, c) + A).to(A)
    yield rewrite(A + Matrix.zero(r, c)).to(A)
    yield rewrite(Matrix.zero(r,c) - A).to( -A)
    yield rewrite(A - Matrix.zero(r,c)).to(A)

    yield rewrite(Matrix.zero(m, r) @ B).to(Matrix.zero(m, c))
    yield rewrite(B @ Matrix.zero(c, m)).to(Matrix.zero(r, m))
    yield rewrite(Matrix.zero(m, c) @ B.T).to(Matrix.zero(m, r))
    yield rewrite(B.T @ Matrix.zero(r, m)).to(Matrix.zero(c, m))
    # yield rewrite(A @ Matrix.zero(d) @ B).to(Matrix.zero(d))
    yield rewrite(Matrix.zero(r, c) + B).to(B)
    yield rewrite(B + Matrix.zero(r, c)).to(B)
    yield rewrite(Matrix.zero(r,c) - B).to( -B)
    yield rewrite(B - Matrix.zero(r,c)).to(B)
    yield rewrite(Matrix.zero(m, r) @ B.A_inverse()).to(Matrix.zero(m, c))
    yield rewrite(B.A_inverse() @ Matrix.zero(c, m)).to(Matrix.zero(r, m))

    yield rewrite(Matrix.zero(m, r) @ C).to(Matrix.zero(m, r))
    yield rewrite(C @ Matrix.zero(r, m)).to(Matrix.zero(r, m))
    yield rewrite(Matrix.zero(m, r) @ C.T).to(Matrix.zero(m, r))
    yield rewrite(C.T @ Matrix.zero(r, m)).to(Matrix.zero(r, m))
    # yield rewrite(A @ Matrix.zero(d) @ B).to(Matrix.zero(d))
    yield rewrite(Matrix.zero(r, r) + C).to(C)
    yield rewrite(C + Matrix.zero(r, r)).to(C)
    yield rewrite(Matrix.zero(r,r) - C).to( -C)
    yield rewrite(C - Matrix.zero(r,r)).to(C)

#--------------------------------------------------------------------------------------------------------------------------------------------------
optimisations_left = ruleset()
@optimisations_left.register
def _id_ops(A : Matrix, B: Matrix, d: i64Like) -> Iterable[RewriteOrRule]:
    yield rewrite(Matrix.identity(d) @ A).to(A)
    yield rewrite(A @ Matrix.identity(d)).to(A)
    yield rewrite(A @ Matrix.identity(d) @ B).to(A @ B)
    yield rewrite((Matrix.identity(d).T)).to(Matrix.identity(d))
    yield rewrite((Matrix.identity(d)).inverse()).to(Matrix.identity(d))
    # yield rewrite((A + Matrix.identity(d)) @ A.inverse()).to(Matrix.identity(d) + A.inverse())

@optimisations_left.register
def _inv_ops(A: Matrix, B: Matrix, d: i64Like, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    yield rewrite(A @ A.inverse() @ B).to(B)
    yield rewrite(B @ A @ A.inverse()).to(B)
    yield rewrite(A @ (A.inverse() @ B)).to(B)
    yield rewrite(A.inverse() @ A @ B).to(B)
    yield rewrite(B @ A.inverse() @ A).to(B)
    yield rewrite(A.inverse() @ (A @ B)).to(B)
    yield rewrite((A @ B).inverse()).to(B.inverse() @ A.inverse())
    yield rewrite(A.inverse().inverse()).to(A)

@optimisations_left.register
def _inv_ops2(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)
    yield rewrite(A.inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.inverse()).to(Matrix.identity(r))
    yield rewrite(B.inverse() @ B).to(Matrix.identity(r))
    yield rewrite(B @ B.inverse()).to(Matrix.identity(r))
    yield rewrite(C.inverse()).to(C)
    yield rewrite(C.inverse() @ C).to(C)
    yield rewrite(C @ C.inverse()).to(C)
    yield rewrite(A - (A @ B)).to(A @ (Matrix.identity(r) - B))
    yield rewrite(B - (B @ A)).to(B @ (Matrix.identity(r) - A))

@optimisations_left.register
def _Ainv_ops(A: Matrix, B: Matrix, d: i64Like, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    yield rewrite(A @ A.A_inverse() @ B).to(B)
    yield rewrite(B @ A @ A.A_inverse()).to(B)
    yield rewrite(A @ (A.A_inverse() @ B)).to(B)
    yield rewrite(A.A_inverse() @ A @ B).to(B)
    yield rewrite(B @ A.A_inverse() @ A).to(B)
    yield rewrite(A.A_inverse() @ (A @ B)).to(B)
    yield rewrite((A @ B).A_inverse()).to(B.A_inverse() @ A.A_inverse())
    yield rewrite(A.A_inverse().A_inverse()).to(A)

@optimisations_left.register
def _Ainv_ops2(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)
    yield rewrite(A.A_inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.A_inverse()).to(Matrix.identity(r))
    yield rewrite(B.A_inverse() @ B).to(Matrix.identity(r))
    yield rewrite(B @ B.A_inverse()).to(Matrix.identity(r))
    yield rewrite(C.A_inverse().A_inverse()).to(C)
    yield rewrite(C.A_inverse() @ C).to(C)
    yield rewrite(C @ C.A_inverse()).to(C)

@optimisations_left.register
def _neg2(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]: 
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)   
    yield rewrite(A - A).to(Matrix.zero(r, c))
    yield rewrite(A + (-A)).to(Matrix.zero(r, c))
    yield rewrite(B - B).to(Matrix.zero(r, c))
    yield rewrite(B + (-B)).to(Matrix.zero(r, c))
    yield rewrite(C - C).to(Matrix.zero(r, r))
    yield rewrite(C + (-C)).to(Matrix.zero(r, r))
    yield rewrite((A.inverse() - A.inverse())).to(Matrix.zero(r, c))
    yield rewrite((B.inverse() - B.inverse())).to(Matrix.zero(r, c))
    yield rewrite((A.A_inverse() - A.A_inverse())).to(Matrix.zero(r, c))
    yield rewrite((B.A_inverse() - B.A_inverse())).to(Matrix.zero(r, c))

@optimisations_left.register
def _neg(A: Matrix, B: Matrix) -> Iterable[RewriteOrRule]:
    # yield rewrite(A - B).to(A + (-B))
    yield rewrite(A - (-B)).to(A + B)
    yield rewrite(A + (-B)).to(A - B)
    yield rewrite(A @ (-B)).to(- (A @ B))
    yield rewrite((-A) @ (B)).to(- (A @ B))
    yield rewrite(-(A + B)).to((-A) + (-B))
    yield rewrite(-(A - B)).to(B - A)
    yield rewrite(-(-A)).to(A)
    yield rewrite(-(A @ B)).to((-A) @ B)
    yield rewrite((-A) + B).to(B - A)

@optimisations_left.register
def _add_assoc(A: Matrix, B: Matrix, C: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A + B).to(B + A)
    yield rewrite((A + B) + C).to(A + (B + C))

@optimisations_left.register
def _mul_assoc(A : Matrix, B: Matrix, C: Matrix) -> Iterable[RewriteOrRule]:
    # yield rewrite((A @ B) @ C).to(A @ (B @ C))
    yield rewrite(A @ (B @ C)).to(A @ B @ C)

@optimisations_left.register
def _mul_distrib(A: Matrix, B: Matrix, C: Matrix, D: Matrix) -> Iterable[RewriteOrRule]:
    yield birewrite((A + B) @ C).to((A @ C) + (B @ C))
    yield birewrite(A @ (B + C)).to((A @ B) + (A @ C))
    yield birewrite((A - B) @ C).to((A @ C) - (B @ C))
    yield birewrite(A @ (B - C)).to((A @ B) - (A @ C))

@optimisations_left.register
def _add_comm(A: Matrix, B: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A + B).to(B + A)

@optimisations_left.register
def __transpose(A: Matrix, B: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A.T.T).to(A)
    yield rewrite((A @ B).T).to(B.T @ A.T)
    yield rewrite((A.T).inverse()).to((A.inverse()).T)
    yield rewrite((A.T).A_inverse()).to((A.A_inverse()).T)
    yield rewrite((A + B).T).to(A.T + B.T)
    yield rewrite((A - B).T).to(A.T - B.T)

@optimisations_left.register
def __sym(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.sym(name, row = r, col = c)
    yield rewrite(A.T).to(A)
    yield rewrite(A.inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.inverse()).to(Matrix.identity(r))
    yield rewrite(A.inverse().T).to(A.inverse())
    yield rewrite(A.A_inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.A_inverse()).to(Matrix.identity(r))
    yield rewrite(A.A_inverse().T).to(A.A_inverse())

@optimisations_left.register
def __zero(name: StringLike, r: i64Like, c: i64Like, m: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)

    yield rewrite(Matrix.zero(r, c).T).to(Matrix.zero(c, r))
    # yield rewrite(Matrix.zero().inverse()).to(Matrix.zero())


    yield rewrite(Matrix.zero(m, r) @ A).to(Matrix.zero(m, c))
    yield rewrite(A @ Matrix.zero(c, m)).to(Matrix.zero(r, m))
    yield rewrite(Matrix.zero(m, c) @ A.T).to(Matrix.zero(m, r))
    yield rewrite(A.T @ Matrix.zero(r, m)).to(Matrix.zero(c, m))
    # yield rewrite(A @ Matrix.zero(d) @ B).to(Matrix.zero(d))
    yield rewrite(Matrix.zero(r, c) + A).to(A)
    yield rewrite(A + Matrix.zero(r, c)).to(A)
    yield rewrite(Matrix.zero(r,c) - A).to( -A)
    yield rewrite(A - Matrix.zero(r,c)).to(A)

    yield rewrite(Matrix.zero(m, r) @ B).to(Matrix.zero(m, c))
    yield rewrite(B @ Matrix.zero(c, m)).to(Matrix.zero(r, m))
    yield rewrite(Matrix.zero(m, c) @ B.T).to(Matrix.zero(m, r))
    yield rewrite(B.T @ Matrix.zero(r, m)).to(Matrix.zero(c, m))
    # yield rewrite(A @ Matrix.zero(d) @ B).to(Matrix.zero(d))
    yield rewrite(Matrix.zero(r, c) + B).to(B)
    yield rewrite(B + Matrix.zero(r, c)).to(B)
    yield rewrite(Matrix.zero(r,c) - B).to( -B)
    yield rewrite(B - Matrix.zero(r,c)).to(B)
    yield rewrite(Matrix.zero(m, r) @ B.A_inverse()).to(Matrix.zero(m, c))
    yield rewrite(B.A_inverse() @ Matrix.zero(c, m)).to(Matrix.zero(r, m))

    yield rewrite(Matrix.zero(m, r) @ C).to(Matrix.zero(m, r))
    yield rewrite(C @ Matrix.zero(r, m)).to(Matrix.zero(r, m))
    yield rewrite(Matrix.zero(m, r) @ C.T).to(Matrix.zero(m, r))
    yield rewrite(C.T @ Matrix.zero(r, m)).to(Matrix.zero(r, m))
    # yield rewrite(A @ Matrix.zero(d) @ B).to(Matrix.zero(d))
    yield rewrite(Matrix.zero(r, r) + C).to(C)
    yield rewrite(C + Matrix.zero(r, r)).to(C)
    yield rewrite(Matrix.zero(r,r) - C).to( -C)
    yield rewrite(C - Matrix.zero(r,r)).to(C)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

id_ops = ruleset()
@id_ops.register
def _id_ops(A : Matrix, B: Matrix, d: i64Like) -> Iterable[RewriteOrRule]:
    yield rewrite(Matrix.identity(d) @ A).to(A)
    yield rewrite(A @ Matrix.identity(d)).to(A)
    yield rewrite(A @ Matrix.identity(d) @ B).to(A @ B)
    yield rewrite((Matrix.identity(d).T)).to(Matrix.identity(d))
    yield rewrite((Matrix.identity(d)).inverse()).to(Matrix.identity(d))
    # yield rewrite((A + Matrix.identity(d)) @ A.inverse()).to(Matrix.identity(d) + A.inverse())

inv_ops = ruleset()
@inv_ops.register
def _inv_ops(A: Matrix, B: Matrix, d: i64Like, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    yield rewrite(A @ A.inverse() @ B).to(B)
    yield rewrite(B @ A @ A.inverse()).to(B)
    yield rewrite(A @ (A.inverse() @ B)).to(B)
    yield rewrite(A.inverse() @ A @ B).to(B)
    yield rewrite(B @ A.inverse() @ A).to(B)
    yield rewrite(A.inverse() @ (A @ B)).to(B)
    yield rewrite((A @ B).inverse()).to(B.inverse() @ A.inverse())
    yield rewrite(A.inverse().inverse()).to(A)

@inv_ops.register
def _inv_ops2(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)
    yield rewrite(A.inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.inverse()).to(Matrix.identity(r))
    yield rewrite(B.inverse() @ B).to(Matrix.identity(r))
    yield rewrite(B @ B.inverse()).to(Matrix.identity(r))
    yield rewrite(C.inverse() @ C).to(Matrix.identity(r))
    yield rewrite(C @ C.inverse()).to(Matrix.identity(r))

neg_ops = ruleset()
@neg_ops.register
def _neg(A: Matrix, B: Matrix) -> Iterable[RewriteOrRule]:
    # yield rewrite(A - B).to(A + (-B))
    yield rewrite(A - (-B)).to(A + B)
    yield rewrite(A + (-B)).to(A - B)
    yield rewrite(A @ (-B)).to(- (A @ B))
    yield rewrite((-A) @ (B)).to(- (A @ B))

@neg_ops.register
def _neg2(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]: 
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)   
    yield rewrite(A - A).to(Matrix.zero(r, c))
    yield rewrite(A + (-A)).to(Matrix.zero(r, c))
    yield rewrite(B - B).to(Matrix.zero(r, c))
    yield rewrite(B + (-B)).to(Matrix.zero(r, c))
    yield rewrite(C - C).to(Matrix.zero(r, r))
    yield rewrite(C + (-C)).to(Matrix.zero(r, r))
    yield rewrite((A.inverse() - A.inverse())).to(Matrix.zero(r, c))
    yield rewrite((B.inverse() - B.inverse())).to(Matrix.zero(r, c))
    yield rewrite((A.A_inverse() - A.A_inverse())).to(Matrix.zero(r, c))
    yield rewrite((B.A_inverse() - B.A_inverse())).to(Matrix.zero(r, c))

add_assoc_ops = ruleset()
@add_assoc_ops.register
def _add_assoc(A: Matrix, B: Matrix, C: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A + B).to(B + A)
    yield rewrite((A + B) + C).to(A + (B + C))

mul_assoc_ops = ruleset()
@mul_assoc_ops.register
def _mul_assoc(A : Matrix, B: Matrix, C: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite((A @ B) @ C).to(A @ (B @ C))
    # yield rewrite(A @ (B @ C)).to(A @(B @ C))

mul_distrib_ops = ruleset()
@mul_distrib_ops.register
def _mul_distrib(A: Matrix, B: Matrix, C: Matrix, D: Matrix) -> Iterable[RewriteOrRule]:
    yield birewrite((A + B) @ C).to(A @ C + B @ C)
    yield birewrite(A @ (B + C)).to(A @ B + A @ C)
    yield birewrite((A - B) @ C).to(A @ C - B @ C)
    yield birewrite(A @ (B - C)).to(A @ B - A @ C)

add_comm_ops = ruleset()
@add_comm_ops.register
def _add_comm(A: Matrix, B: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A + B).to(B + A)

transpose_ops = ruleset()
@transpose_ops.register
def __transpose(A: Matrix, B: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A.T.T).to(A)
    yield rewrite((A @ B).T).to(B.T @ A.T)
    yield rewrite((A.T).inverse()).to((A.inverse()).T)
    yield rewrite((A + B).T).to(A.T + B.T)
    yield rewrite((A - B).T).to(A.T - B.T)

sym_ops = ruleset()
@sym_ops.register
def __sym(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.sym(name, row = r, col = c)
    yield rewrite(A.T).to(A)
    yield rewrite(A.inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.inverse()).to(Matrix.identity(r))
    yield rewrite(A.inverse().T).to(A.inverse())
    yield rewrite(A.A_inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.A_inverse()).to(Matrix.identity(r))
    yield rewrite(A.A_inverse().T).to(A.A_inverse())

zero_ops = ruleset()
@zero_ops.register
def __zero(name: StringLike, r: i64Like, c: i64Like, m: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)

    yield rewrite(Matrix.zero(r, c).T).to(Matrix.zero(r, c))
    # yield rewrite(Matrix.zero().inverse()).to(Matrix.zero())


    yield rewrite(Matrix.zero(m, r) @ A).to(Matrix.zero(m, c))
    yield rewrite(A @ Matrix.zero(c, m)).to(Matrix.zero(r, m))
    yield rewrite(Matrix.zero(m, c) @ A.T).to(Matrix.zero(m, r))
    yield rewrite(A.T @ Matrix.zero(r, m)).to(Matrix.zero(c, m))
    # yield rewrite(A @ Matrix.zero(d) @ B).to(Matrix.zero(d))
    yield rewrite(Matrix.zero(r, c) + A).to(A)
    yield rewrite(A + Matrix.zero(r, c)).to(A)
    yield rewrite(Matrix.zero(r,c) - A).to( -A)
    yield rewrite(A - Matrix.zero(r,c)).to(A)

    yield rewrite(Matrix.zero(m, r) @ B).to(Matrix.zero(m, c))
    yield rewrite(B @ Matrix.zero(c, m)).to(Matrix.zero(r, m))
    # yield rewrite(A @ Matrix.zero(d) @ B).to(Matrix.zero(d))
    yield rewrite(Matrix.zero(r, c) + B).to(B)
    yield rewrite(B + Matrix.zero(r, c)).to(B)
    yield rewrite(Matrix.zero(r,c) - B).to( -B)
    yield rewrite(B - Matrix.zero(r,c)).to(B)

    yield rewrite(Matrix.zero(m, r) @ C).to(Matrix.zero(m, r))
    yield rewrite(C @ Matrix.zero(r, m)).to(Matrix.zero(r, m))
    # yield rewrite(A @ Matrix.zero(d) @ B).to(Matrix.zero(d))
    yield rewrite(Matrix.zero(r, r) + C).to(C)
    yield rewrite(C + Matrix.zero(r, r)).to(C)
    yield rewrite(Matrix.zero(r,r) - C).to( -C)
    yield rewrite(C - Matrix.zero(r,r)).to(C)

    yield rewrite(A - A).to(Matrix.zero(r, c))
    yield rewrite(A + (-A)).to(Matrix.zero(r, c))
    yield rewrite(B - B).to(Matrix.zero(r, c))
    yield rewrite(B + (-B)).to(Matrix.zero(r, c))
    yield rewrite(C - C).to(Matrix.zero(r, r))
    yield rewrite(C + (-C)).to(Matrix.zero(r, r))
    
#--------------------------------------------------------------------------------------------------------------------------------------------------
rules_first_step = ruleset()
@rules_first_step.register
def _id_ops(A : Matrix, B: Matrix, d: i64Like) -> Iterable[RewriteOrRule]:
    yield rewrite(Matrix.identity(d) @ A).to(A)
    yield rewrite(A @ Matrix.identity(d)).to(A)
    yield rewrite(A @ Matrix.identity(d) @ B).to(A @ B)
    yield rewrite((Matrix.identity(d).T)).to(Matrix.identity(d))
    yield rewrite((Matrix.identity(d)).inverse()).to(Matrix.identity(d))
    # yield rewrite((A + Matrix.identity(d)) @ A.inverse()).to(Matrix.identity(d) + A.inverse())

@rules_first_step.register
def _inv_ops(A: Matrix, B: Matrix, d: i64Like, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    yield rewrite(A @ A.inverse() @ B).to(B)
    yield rewrite(B @ A @ A.inverse()).to(B)
    yield rewrite(A @ (A.inverse() @ B)).to(B)
    yield rewrite(A.inverse() @ A @ B).to(B)
    yield rewrite(B @ A.inverse() @ A).to(B)
    yield rewrite(A.inverse() @ (A @ B)).to(B)
    yield rewrite((A @ B).inverse()).to(B.inverse() @ A.inverse())
    yield rewrite(A.inverse().inverse()).to(A)

@rules_first_step.register
def _inv_ops2(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)
    yield rewrite(A.inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.inverse()).to(Matrix.identity(r))
    yield rewrite(B.inverse() @ B).to(Matrix.identity(r))
    yield rewrite(B @ B.inverse()).to(Matrix.identity(r))
    yield rewrite(C.inverse() @ C).to(Matrix.identity(r))
    yield rewrite(C @ C.inverse()).to(Matrix.identity(r))

@rules_first_step.register
def _Ainv_ops(A: Matrix, B: Matrix, d: i64Like, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    yield rewrite(A @ A.A_inverse() @ B).to(B)
    yield rewrite(B @ A @ A.A_inverse()).to(B)
    yield rewrite(A @ (A.A_inverse() @ B)).to(B)
    yield rewrite(A.A_inverse() @ A @ B).to(B)
    yield rewrite(B @ A.A_inverse() @ A).to(B)
    yield rewrite(A.A_inverse() @ (A @ B)).to(B)
    yield rewrite((A @ B).A_inverse()).to(B.A_inverse() @ A.A_inverse())
    yield rewrite(A.A_inverse().A_inverse()).to(A)

@rules_first_step.register
def _Ainv_ops2(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.named(name, r, c)
    B = Matrix.sym(name, r, c)
    C = Matrix.identity(r)
    yield rewrite(A.A_inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.A_inverse()).to(Matrix.identity(r))
    yield rewrite(B.A_inverse() @ B).to(Matrix.identity(r))
    yield rewrite(B @ B.A_inverse()).to(Matrix.identity(r))
    yield rewrite(C.A_inverse().A_inverse()).to(C)
    yield rewrite(C.A_inverse() @ C).to(C)
    yield rewrite(C @ C.A_inverse()).to(C)

@rules_first_step.register
def _neg(A: Matrix, B: Matrix) -> Iterable[RewriteOrRule]:
    # yield rewrite(A - B).to(A + (-B))
    yield rewrite(A - (-B)).to(A + B)
    yield rewrite(A + (-B)).to(A - B)
    yield rewrite(A @ (-B)).to(- (A @ B))
    yield rewrite((-A) @ (B)).to(- (A @ B))

@rules_first_step.register
def _add_assoc(A: Matrix, B: Matrix, C: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A + B).to(B + A)
    yield rewrite((A + B) + C).to(A + (B + C))

@rules_first_step.register
def _mul_assoc(A : Matrix, B: Matrix, C: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite((A @ B) @ C).to(A @ (B @ C))
    # yield rewrite(A @ (B @ C)).to(A @(B @ C))

@rules_first_step.register
def _mul_distrib(A: Matrix, B: Matrix, C: Matrix, D: Matrix) -> Iterable[RewriteOrRule]:
    yield birewrite((A + B) @ C).to((A @ C) + (B @ C))
    yield birewrite(A @ (B + C)).to((A @ B) + (A @ C))
    yield birewrite((A - B) @ C).to((A @ C) - (B @ C))
    yield birewrite(A @ (B - C)).to((A @ B) - (A @ C))

@rules_first_step.register
def _add_comm(A: Matrix, B: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite(A + B).to(B + A)

@rules_first_step.register
def __sym(name: StringLike, r: i64Like, c: i64Like) -> Iterable[RewriteOrRule]:
    A = Matrix.sym(name, row = r, col = c)
    yield rewrite(A.T).to(A)
    yield rewrite(A.inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.inverse()).to(Matrix.identity(r))
    yield rewrite(A.inverse().T).to(A.inverse())
    yield rewrite(A.A_inverse() @ A).to(Matrix.identity(r))
    yield rewrite(A @ A.A_inverse()).to(Matrix.identity(r))
    yield rewrite(A.A_inverse().T).to(A.A_inverse())
#--------------------------------------------------------------------------------------------------------------------------------------------------

rules_rearrangement = ruleset()
@rules_rearrangement.register
def _mul_distrib(A: Matrix, B: Matrix, C: Matrix, D: Matrix) -> Iterable[RewriteOrRule]:
    yield birewrite((A + B) @ C).to((A @ C) + (B @ C))
    yield birewrite(A @ (B + C)).to((A @ B) + (A @ C))
    yield birewrite((A - B) @ C).to((A @ C) - (B @ C))
    yield birewrite(A @ (B - C)).to((A @ B) - (A @ C))

@rules_rearrangement.register
def _mul_assoc(A : Matrix, B: Matrix, C: Matrix) -> Iterable[RewriteOrRule]:
    yield rewrite((A @ B) @ C).to(A @ (B @ C))
    # yield rewrite(A @ (B @ C)).to(A @(B @ C))

#--------------------------------------------------------------------------------------------------------------------------------------------------
analysis = ruleset()
@analysis.register
def _shape(A: Matrix, B: Matrix, C: Matrix, r: i64, m:i64, c:i64, name: StringLike) -> Iterable[RewriteOrRule]:
    # yield rule(A == Matrix(r, c)).then(set_(A.row).to(r), set_(A.col).to(c))
    yield rule(A == Matrix.named(name, r, c)).then(set_(A.row).to(r), set_(A.col).to(c))
    yield rule(A == Matrix.sym(name, r, c)).then(set_(A.row).to(r), set_(A.col).to(c))
    yield rule(A == Matrix.identity(r)).then(set_(A.row).to(r), set_(A.col).to(r))
    yield rule(A == Matrix.zero(r, c)).then(set_(A.row).to(r), set_(A.col).to(c))
    # yield rule(A == Matrix.named(name, r, c).T).then(set_(A.row).to(c), set_(A.col).to(r))
    # yield rule(A == Matrix.sym(name, r, c).T).then(set_(A.row).to(c), set_(A.col).to(r))
    # yield rule(A == Matrix.identity(r).T).then(set_(A.row).to(r), set_(A.col).to(r))

    yield rule(
        C == (A @ B),
        r == A.row,
        m == A.col,
        eq(m).to(B.row),
        c == B.col,
    ).then(set_(C.row).to(r), set_(C.col).to(c))

    yield rule(
        C == (A + B),
        r == A.row,
        A.col == B.row,
        c == B.col,
    ).then(set_(C.row).to(r), set_(C.col).to(c))

    yield rule(
        C == (A - B),
        r == A.row,
        A.col == B.row,
        c == B.col,
    ).then(set_(C.row).to(r), set_(C.col).to(c))

    yield rule(
        C == A.T,
        r == A.row,
        c == A.col,
    ).then(set_(C.row).to(c), set_(C.col).to(r))

    yield rule(
        C == -A,
        r == A.row,
        c == A.col,
    ).then(set_(C.row).to(r), set_(C.col).to(c))

    yield rule(
        C == A.inverse(),
        r == A.row,
        c == A.col,
    ).then(set_(C.row).to(r), set_(C.col).to(c))

    yield rule(
        C == A.A_inverse(),
        r == A.row,
        c == A.col,
    ).then(set_(C.row).to(r), set_(C.col).to(c))

    yield rule(
        C == A.ltrisolve(),
        r == A.row,
        c == A.col,
    ).then(set_(C.row).to(r), set_(C.col).to(c))


    yield rule(C == A @ B, r == A.row, m == A.col, c == B.col).then(set_cost(A @ B, r * m * c))
    yield rule(C == A + B, r == A.row, m == A.col).then(set_cost(A + B, r * m))
    yield rule(C == A - B, r == A.row, m == A.col).then(set_cost(A - B, r * m))
    yield rule(C == A.inverse(), r == A.row, m == A.col).then(set_cost(A.inverse(), r * r * r))
    yield rule(C == A.ltrisolve(), r == A.row, m == A.col).then(set_cost(A.ltrisolve(), r * r))
    yield rule(C == A.A_inverse(), r == A.row, m == A.col).then(set_cost(A.A_inverse(), 10000 * r * r * r))
    yield rule(C == - A, r == A.row, m == A.col).then(set_cost(-A , 1))
    yield rule(C == A.T, r == A.row, m == A.col).then(set_cost(A.T , 1))


    # yield rule(A @ B.T, r == A.row, m == A.col, c == B.row).then(set_cost(A @ B.T, (r * m * c) + 1))
    # yield rule(A.T @ B, r == A.col, m == A.row, c == B.col).then(set_cost(A.T @ B, (r * m * c) + 1))
    # yield rule(C == A @ B.inverse(), r == A.row, m == A.col, c == B.row).then(set_cost(A @ B.inverse(), (r * m * c) + (c * c * c)))
    # yield rule(C == A.inverse() @ B, r == A.col, m == A.row, c == B.col).then(set_cost(A.inverse() @ B, (r * m * c) + (r * r * r)))
    # yield rule(C == A.inverse() @ B.inverse(), r == A.col, m == A.row, c == B.col).then(set_cost(A.inverse() @ B.inverse(), (r * m * c) + (r * r * r) + (r * r * r)))
    # yield birewrite(A @ (B @ C)).to((A @ B) @ C)











#-----------------------------------Optimisation functions---------------------------------------------------------------------------------------------------------------------------------------


def get_VD_expr(graph: polytree, Adim: float | int, Vrow: float | int, A: np.ndarray, egglog_step2_runs = 12):


        Amat = Matrix.sym('Amat', row = Adim, col = Adim)

        expr = Amat.A_inverse()
        ex1, val_dict = tracer_to_egraph(graph, expr=expr, Adim = Adim, A = A)
        egraph = EGraph()
        egraph.register(ex1)
        egraph.run(analysis.saturate())
        egraph.run(rules_first_step.saturate())
        egraph.run(optimisations)
        egraph.run(analysis.saturate())
        MAinv = egraph.extract(ex1)

        ic('step 1 done')

        D1 = MAinv - Amat.A_inverse()
        egraph2 = EGraph()
        egraph2.register(D1)
        egraph2.run(analysis.saturate())
        for i in range(egglog_step2_runs):
            ic(i)
            egraph2.run(optimisations)
        egraph2.run(zero_ops.saturate())
        egraph2.run(analysis.saturate())
        D1_s = egraph2.extract(D1)

        ic('step 2 done')

        V = Matrix.named('V', row = Vrow, col = Adim)
        VD = V @ D1_s 
        egraph3 = EGraph()
        egraph3.register(VD)
        egraph3.run(analysis.saturate())
        # for i in range(50):
        #     # ic(i)
        #     egraph3.run(optimisations_left)
        egraph3.run(optimisations_left.saturate())
        egraph3.run(optimisations)
        egraph3.run(analysis.saturate())
        ex_final_s = egraph3.extract(VD)
        ex_VD = - ex_final_s

        return ex_VD, val_dict


def get_DV_expr(graph: polytree, Adim: float | int, Vrow: float | int, A: np.ndarray, egglog_step2_runs = 12):

    Amat = Matrix.sym('Amat', row = Adim, col = Adim)

    expr = Amat.A_inverse()
    ex1, val_dict = tracer_to_egraph(graph, expr=expr, Adim = Adim, A = A)
    egraph = EGraph()
    egraph.register(ex1)
    egraph.run(analysis.saturate())
    egraph.run(rules_first_step.saturate())
    egraph.run(optimisations)
    egraph.run(analysis.saturate())
    MAinv = egraph.extract(ex1)

    ic('step 1 done')

    D1 = MAinv - Amat.A_inverse()
    egraph2 = EGraph()
    egraph2.register(D1)
    egraph2.run(analysis.saturate())
    for i in range(egglog_step2_runs):
        ic(i)
        egraph2.run(optimisations)
    egraph2.run(zero_ops.saturate())
    egraph2.run(analysis.saturate())
    D1_s = egraph2.extract(D1)

    ic('step 2 done')

    V = Matrix.named('V', row = Vrow, col = Adim)
    ex_final = D1_s @ V.T 
    egraph4 = EGraph()
    egraph4.register(ex_final)
    egraph4.run(analysis.saturate())
    egraph4.run(optimisations.saturate())
    egraph4.run(analysis)
    ex_final_s = egraph4.extract(ex_final)
    ex_VD = - ex_final_s

    return ex_VD, val_dict

# @line_profiler.profile
def eval_expr(expr, val_dict, cache_dict = None, expr_refs = None): 

    # ic(val_dict)
    # ic(val_dict['V'].shape)
    # ic('here!!!!!!!!!!!')
    # ic(len(cache_dict))
    # # ic.disable()
    if cache_dict is None:
        cache_dict = {}
        expr_refs = {}

    cache_key = id(expr)
    if cache_key in cache_dict:
        return cache_dict[cache_key]

    expr_refs[cache_key] = expr
    arg = expr
    # ic(expr)
    if get_callable_fn(arg) == Matrix.named:
        val_name = get_literal_value(get_callable_args(arg)[0])
        val = val_dict[val_name]
        cache_dict[cache_key] = val
        return val

    elif get_callable_fn(arg) == Matrix.sym:
        val_name = get_literal_value(get_callable_args(arg)[0])
        val = val_dict[val_name]
        cache_dict[cache_key] = val
        return val

    elif get_callable_fn(arg) == Matrix.identity:
        # val = val_dict['Id']
        # ic(get_callable_args(arg))
        dim = int(get_callable_args(arg)[0])
        val = np.eye(dim)
        cache_dict[cache_key] = val
        return val
    
    elif get_callable_fn(arg) == Matrix.zero:
        val = 0
        cache_dict[cache_key] = val
        return val        
    
    elif get_callable_fn(arg) == Matrix.ltrisolve:
        # ic('here ltrisolve')
        inner = get_callable_args(arg)[0]
        inner_val = eval_expr(inner, val_dict, cache_dict, expr_refs)
        dim = inner_val.shape[0]
        # ic(dim)
        val = scipy.linalg.solve_triangular(inner_val, np.eye(dim), lower = True, check_finite = False)
        cache_dict[cache_key] = val
        return val

    else:
        fun = get_callable_fn(expr)
        # ic(fun)
        # ic(expr)
        raw_args = get_callable_args(expr)
        # ic(fun, raw_args)
        if fun == Matrix.__matmul__:
            args = None
            val = apply_fun(fun, args, val_dict, cache_dict, raw_args = raw_args, expr_refs = expr_refs)
        else:
            args = [eval_expr(a, val_dict, cache_dict, expr_refs) for a in get_callable_args(expr)]
            val = apply_fun(fun, args, val_dict, cache_dict, raw_args = raw_args, expr_refs = expr_refs)
        # ic(fun)
        cache_dict[cache_key] = val
        return val


# @line_profiler.profile
def apply_fun(fun, args, val_dict, cache_dict, expr_refs, raw_args = None):
    # ic(fun, args)
    # ic.enable()
    if fun == Matrix.__add__:
        # ic('add')
        return args[0] + args[1]
    elif fun == Matrix.__radd__:
        # ic('add2')
        return args[1] + args[0]
    
    elif fun == Matrix.__sub__:
        # ic('sub')
        # ic(args[0])
        # ic(args[1])
        return args[0] - args[1]
    
    elif fun == Matrix.__rsub__:
        # ic('rsub')
        # ic(args[0])
        # ic(args[1])
        return args[1] - args[0]

    elif fun == Matrix.__neg__:
        # ic('neg')
        # ic(raw_args)
        try:
            val = -args[0]
            # ic(val)
        except: 
            val = None
            # ic(val)
        return val
    
    # if fun == Matrix.inverse:
    #     ic('inv')
    #     ic('shouldnt be here---------------------------------------')
    #     # ic(args[0])
    #     Ainv = np.linalg.inv(args[0])
    #     return Ainv
    
    # if fun == Matrix.ltrisolve:
    #     ic('tinv')
    #     ic('shouldnt be here---------------------------------------')
    #     # ic(args[0])
    #     Ainvt = np.linalg.inv(args[0])
    #     # Ainvt = 
    #     return Ainvt

    elif fun == Matrix.__matmul__:
        # ic('matmul')
        # ic(args[0].shape)
        # ic(args[1].shape)
        # ic(raw_args)
        # ic(args[0])
        # ic(args[1])
        if raw_args is not None:
            # ic('here1')
            left, right = raw_args
            # ic(get_callable_fn(left))
            fun_left = get_callable_fn(left)
            fun_right = get_callable_fn(right)
            if fun_left == Matrix.inverse:
                # ic('here1a')
                # ic('here')
                # ic(right)
                # ic(left)
                # ic('---------')
                # ic(args[0])
                # ic(args[1])
                # ic(cache_dict[str(right)])
                # ic(cache_dict[str(left)])
                left_eval = eval_expr(get_callable_args(left)[0], val_dict, cache_dict, expr_refs)
                right_eval = eval_expr(right, val_dict, cache_dict, expr_refs)
                # ic(left_eval.shape)
                # ic(right_eval.shape)
                val = np.linalg.solve(left_eval, right_eval)


            elif fun_right == Matrix.inverse:
                # ic('here2')
                # ic('here1b')
                right_eval = eval_expr(get_callable_args(right)[0], val_dict, cache_dict, expr_refs)
                left_eval = eval_expr(left, val_dict, cache_dict, expr_refs)
                val = np.linalg.solve(right_eval.T, left_eval.T).T        

            elif fun_left == Matrix.ltrisolve:
                # ic('here1c')
                left_eval = eval_expr(get_callable_args(left)[0], val_dict, cache_dict, expr_refs)
                right_eval = eval_expr(right, val_dict, cache_dict, expr_refs)
                # ic(left_eval.shape)
                # ic(right_eval.shape)
                # ic(left_eval.shape)
                # ic(right_eval.shape)
                val = scipy.linalg.solve_triangular(left_eval, right_eval, lower = True, check_finite = False)

            elif fun_right == Matrix.ltrisolve:
                # ic('here21')
                # ic('here1d')
                right_eval = eval_expr(get_callable_args(right)[0], val_dict, cache_dict, expr_refs)
                left_eval = eval_expr(left, val_dict, cache_dict, expr_refs)
                # ic(right_eval.shape)
                # ic(left_eval.shape)
                val = scipy.linalg.solve_triangular(right_eval.T, left_eval.T, check_finite = False).T        

            elif fun_left == Matrix.__neg__:
                # ic('here1e')
                # ic('here3--------------------------------')
                inner = get_callable_args(left)[0]
                fun_inner = get_callable_fn(inner)
                # ic(inner)
                if fun_inner == Matrix.inverse:
                    left_eval = eval_expr(get_callable_args(inner)[0], val_dict, cache_dict, expr_refs)
                    right_eval = eval_expr(right, val_dict, cache_dict, expr_refs)
                    val = - np.linalg.solve(left_eval, right_eval)
                elif fun_inner == Matrix.ltrisolve:
                    left_eval = eval_expr(get_callable_args(inner)[0], val_dict, cache_dict, expr_refs)
                    right_eval = eval_expr(right, val_dict, cache_dict, expr_refs)
                    val = - scipy.linalg.solve_triangular(left_eval, right_eval, lower = True, check_finite = False)
                # this may or may not be correct - need to check
                else: 
                    left_eval = eval_expr(get_callable_args(inner)[0], val_dict, cache_dict, expr_refs)
                    right_eval = eval_expr(right, val_dict, cache_dict, expr_refs)
                    val = -left_eval @ right_eval


            elif fun_right == Matrix.__neg__:
                # ic('here1f')
                inner = get_callable_args(right)[0]
                fun_inner = get_callable_fn(inner)
                if fun_inner == Matrix.inverse:
                    right_eval = eval_expr(get_callable_args(inner)[0], val_dict, cache_dict, expr_refs)
                    left_eval = eval_expr(left, val_dict, cache_dict, expr_refs)
                    val = - np.linalg.solve(right_eval.T, left_eval.T).T
                elif fun_inner == Matrix.ltrisolve:
                    right_eval = eval_expr(get_callable_args(inner)[0], val_dict, cache_dict, expr_refs)
                    left_eval = eval_expr(left, val_dict, cache_dict, expr_refs)
                    val = - scipy.linalg.solve_triangular(right_eval.T, left_eval.T, check_finite = False).T
                # this may or may not be correct - need to check
                else:
                    right_eval = eval_expr(get_callable_args(inner)[0], val_dict, cache_dict, expr_refs)
                    left_eval = eval_expr(left, val_dict, cache_dict, expr_refs)
                    # ic(left_eval.shape)
                    # ic(right_eval.shape)
                    val = -(left_eval @ right_eval).T

            else:
                # ic(args[0])
                # ic(args[1])
                # ic(raw_args)
                left_eval = eval_expr(left, val_dict, cache_dict, expr_refs)
                right_eval = eval_expr(right, val_dict, cache_dict, expr_refs)
                val = left_eval @ right_eval
        else:
            # ic('here4')
            val = args[0] @ args[1]
        # val = args[0] @ args[1]
        # ic(val)
        return val
    
    elif fun == Matrix.__rmatmul__:
        # ic('rmatmul')
        return args[1] @ args[0]

    elif fun == Matrix.T:
        # ic('transpose')
        return args[0].T


def tracer_to_egraph(graph, Adim, expr, A):
    # expr = None
    val_dict = {}
    val_dict["Amat"] = A


    for node_local in graph.nodes:
        # expr = node_to_egraph(node_local, expr)
        # ic(node_local.operation)
        # ic(node_local)
        # ic(expr)
        expr, val_dict = node_local.operation.build_expr(node_local = node_local, expr = expr, val_dict = val_dict, Adim = Adim)
        # reset graph?

    

    return expr, val_dict