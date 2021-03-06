# Copyright 2019 The TensorNetwork Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import math
import numpy as np
import torch
from tensornetwork.backends.pytorch import decompositions


def test_expected_shapes():
  val = torch.zeros((2, 3, 4, 5))
  u, s, vh, _ = decompositions.svd_decomposition(torch, val, 2)
  assert u.shape_tensor == (2, 3, 6)
  assert s.shape_tensor == (6,)
  np.testing.assert_allclose(s, np.zeros(6))
  assert vh.shape_tensor == (6, 4, 5)


def test_expected_shapes_qr():
  val = torch.zeros((2, 3, 4, 5))
  q, r = decompositions.qr_decomposition(torch, val, 2)
  assert q.shape_tensor == (2, 3, 6)
  assert r.shape_tensor == (6, 4, 5)


def test_expected_shapes_rq():
  val = torch.zeros((2, 3, 4, 5))
  r, q = decompositions.rq_decomposition(torch, val, 2)
  assert r.shape_tensor == (2, 3, 6)
  assert q.shape_tensor == (6, 4, 5)


def test_rq_decomposition():
  random_matrix = torch.rand([10, 10], dtype=torch.float64)
  r, q = decompositions.rq_decomposition(torch, random_matrix, 1)
  np.testing.assert_allclose(r.mm(q), random_matrix)


def test_qr_decomposition():
  random_matrix = torch.rand([10, 10], dtype=torch.float64)
  q, r = decompositions.qr_decomposition(torch, random_matrix, 1)
  np.testing.assert_allclose(q.mm(r), random_matrix)


def test_max_singular_values():
  np.random.seed(2018)
  random_matrix = np.random.rand(10, 10)
  unitary1, _, unitary2 = np.linalg.svd(random_matrix)
  singular_values = np.array(range(10))
  val = unitary1.dot(np.diag(singular_values).dot(unitary2.T))
  u, s, vh, trun = decompositions.svd_decomposition(
      torch, torch.tensor(val), 1, max_singular_values=7)
  assert u.shape_tensor == (10, 7)
  assert s.shape_tensor == (7,)
  np.testing.assert_array_almost_equal(s, np.arange(9, 2, -1))
  assert vh.shape_tensor == (7, 10)
  np.testing.assert_array_almost_equal(trun, np.arange(2, -1, -1))


def test_max_truncation_error():
  np.random.seed(2019)
  random_matrix = np.random.rand(10, 10)
  unitary1, _, unitary2 = np.linalg.svd(random_matrix)
  singular_values = np.array(range(10))
  val = unitary1.dot(np.diag(singular_values).dot(unitary2.T))
  u, s, vh, trun = decompositions.svd_decomposition(
      torch, torch.Tensor(val), 1, max_truncation_error=math.sqrt(5.1))
  assert u.shape_tensor == (10, 7)
  assert s.shape_tensor == (7,)
  np.testing.assert_array_almost_equal(s, np.arange(9, 2, -1), decimal=5)
  assert vh.shape_tensor == (7, 10)
  np.testing.assert_array_almost_equal(trun, np.arange(2, -1, -1))
