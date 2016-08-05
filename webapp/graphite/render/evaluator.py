import datetime
import time
from django.conf import settings
from graphite.render.grammar import grammar
from graphite.logger import log
from graphite.render.datalib import fetchData, TimeSeries

def evaluateTarget(requestContext, target):
  tokens = grammar.parseString(target)
  result = evaluateTokens(requestContext, tokens)

  if type(result) is TimeSeries:
    return [result] #we have to return a list of TimeSeries objects

  else:
    return result


def evaluateTokens(requestContext, tokens):
  if tokens.expression:
    return evaluateTokens(requestContext, tokens.expression)

  elif tokens.pathExpression:
    return fetchData(requestContext, tokens.pathExpression)

  elif tokens.call:
    try:
      func = SeriesFunctions[tokens.call.func]
      args = [evaluateTokens(requestContext, arg) for arg in tokens.call.args]
      return func(requestContext, *args)
    except ValueError:
      log.exception('value error when render') 
      return []

  elif tokens.number:
    if tokens.number.integer:
      return int(tokens.number.integer)
    elif tokens.number.float:
      return float(tokens.number.float)
    elif tokens.number.scientific:
      return float(tokens.number.scientific[0])

  elif tokens.string:
    return tokens.string[1:-1]

  elif tokens.boolean:
    return tokens.boolean[0] == 'true'


#Avoid import circularities
from graphite.render.functions import SeriesFunctions
