import React, { useEffect, useState, useCallback } from "react"
import "tailwindcss/tailwind.css"

interface LoadingProps {
  time: number // Time in seconds until reaching 99%
}

const Loading: React.FC<LoadingProps> = ({ time }) => {
  const [progress, setProgress] = useState(0)

  const getRandomIncrement = useCallback(() => {
    // Bigger jumps at the start, smaller towards the end
    const remainingProgress = 99 - progress
    const maxJump = Math.max(remainingProgress / 3, 2) // Never jump less than 2%
    return Math.random() * maxJump
  }, [progress])

  const getRandomDelay = useCallback(() => {
    // More frequent updates at start, slower towards end
    const baseDelay = (time * 1000) / 20 // Roughly 20 jumps total
    const variability = baseDelay * 0.5 // 50% variability
    return baseDelay + (Math.random() * variability - variability / 2)
  }, [time])

  useEffect(() => {
    let timeoutId: NodeJS.Timeout | null = null

    const scheduleNextIncrement = () => {
      if (progress >= 99) return

      const delay = getRandomDelay()
      timeoutId = setTimeout(() => {
        setProgress((prev) => {
          const next = Math.min(prev + getRandomIncrement(), 98)
          if (next < 98) scheduleNextIncrement()
          return next
        })
      }, delay)
    }

    scheduleNextIncrement()

    // Schedule the final jump to 99% at the specified time
    const finalTimeout = setTimeout(() => {
      setProgress(99)
    }, time * 1000)

    return () => {
      if (timeoutId) clearTimeout(timeoutId)
      clearTimeout(finalTimeout)
    }
  }, [time, getRandomIncrement, getRandomDelay, progress])

  // Determine animation class based on whether we just had an increment
  const textClass =
    progress === 99
      ? "text-lg font-medium text-gray-800"
      : "text-lg font-medium text-gray-800 animate-pulse"

  return (
    <div className="flex flex-col items-center justify-center h-fit w-48 py-2">
      <div className={textClass}>Loading... {Math.floor(progress)}%</div>
      <div className="w-3/4 h-2 bg-gray-300 rounded-full overflow-hidden mt-6">
        <div
          className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full transition-all duration-75"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  )
}

export default Loading
