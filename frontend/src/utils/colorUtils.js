function hexToRgb(color) {
    if (!color) return "255,255,255"

    if (color.startsWith("rgb")) {
      return color.replace(/[rgba()]/g, "")
    }

    const clean = color.replace('#', '')
    const bigint = parseInt(clean, 16)

    const r = (bigint >> 16) & 255
    const g = (bigint >> 8) & 255
    const b = bigint & 255

    return `${r}, ${g}, ${b}`
}

export { hexToRgb }