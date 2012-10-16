/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.ambari.server.controller.predicate;

import org.apache.ambari.server.controller.spi.PropertyId;

import java.util.Set;

/**
 * Predicate that operates on one other predicate.
 */
public abstract class UnaryPredicate implements BasePredicate {
  private final BasePredicate predicate;

  public UnaryPredicate(BasePredicate predicate) {
    assert(predicate != null);
    this.predicate = predicate;
  }

  public BasePredicate getPredicate() {
    return predicate;
  }

  @Override
  public Set<PropertyId> getPropertyIds() {
    return predicate.getPropertyIds();
  }

  @Override
  public void accept(PredicateVisitor visitor) {
    visitor.acceptUnaryPredicate(this);
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof UnaryPredicate)) return false;

    UnaryPredicate that = (UnaryPredicate) o;

    return predicate.equals(that.predicate);
  }

  @Override
  public int hashCode() {
    return predicate.hashCode();
  }

  public abstract String getOperator();
}
