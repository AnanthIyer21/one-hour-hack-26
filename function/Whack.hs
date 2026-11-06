-- WHACK 26 One Hour Hack: the whack() function. Call it, don't change it.
--   import Whack (whack)
--   main = do
--     ws <- whack
--     print ws
-- Only needs base. It has no random numbers, so the clock is turned into some below.
module Whack (whack) where

import Data.Bits (shiftR, xor)
import Data.List (unfoldr)
import Data.Word (Word64)
import GHC.Clock (getMonotonicTimeNSec)

wordList :: [String]
wordList =
  [ "whack", "hack", "duck", "quack", "goose", "honk", "bug", "feature"
  , "warwick", "oculus", "compsoc", "marshall", "wace", "brevan", "howard", "capital", "one"
  , "bloomberg", "netcraft", "incident", "io", "pizza", "coffee", "sleep", "deploy"
  , "merge", "conflict", "commit", "push", "prod", "segfault", "null", "pointer", "stack"
  , "overflow", "semicolon", "rubber", "demo", "pitch", "prize", "midnight", "wifi"
  ]

-- | Writes 1-100 random words to a file called "whack" (one per line) and returns them.
whack :: IO [String]
whack = do
  seed <- getMonotonicTimeNSec
  let (n, seed') = splitMix seed
      count = 1 + fromIntegral (n `mod` 100)
      picks = take count (unfoldr (Just . splitMix) seed')
      ws = [wordList !! fromIntegral (r `mod` fromIntegral (length wordList)) | r <- picks]
  writeFile "whack" (unlines ws)
  pure ws

-- SplitMix64: returns a random number and the next seed.
splitMix :: Word64 -> (Word64, Word64)
splitMix s = (z3, s')
  where
    s' = s + 0x9E3779B97F4A7C15
    z1 = (s' `xor` (s' `shiftR` 30)) * 0xBF58476D1CE4E5B9
    z2 = (z1 `xor` (z1 `shiftR` 27)) * 0x94D049BB133111EB
    z3 = z2 `xor` (z2 `shiftR` 31)
