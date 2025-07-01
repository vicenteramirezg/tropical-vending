/**
 * Date utility functions for handling timezone-aware operations
 * All functions work with America/New_York timezone to match backend
 */

/**
 * Get current date/time in New York timezone formatted for datetime-local input
 * @returns {string} Date string in YYYY-MM-DDTHH:MM format
 */
export function getCurrentDateTimeLocal() {
  const now = new Date();
  // Convert to New York timezone
  const nyTime = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}));
  
  // Format for datetime-local input (YYYY-MM-DDTHH:MM)
  const year = nyTime.getFullYear();
  const month = String(nyTime.getMonth() + 1).padStart(2, '0');
  const day = String(nyTime.getDate()).padStart(2, '0');
  const hours = String(nyTime.getHours()).padStart(2, '0');
  const minutes = String(nyTime.getMinutes()).padStart(2, '0');
  
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

/**
 * Get current date in New York timezone formatted for date input
 * @returns {string} Date string in YYYY-MM-DD format
 */
export function getCurrentDateLocal() {
  const now = new Date();
  // Convert to New York timezone
  const nyTime = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}));
  
  // Format for date input (YYYY-MM-DD)
  const year = nyTime.getFullYear();
  const month = String(nyTime.getMonth() + 1).padStart(2, '0');
  const day = String(nyTime.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
}

/**
 * Format a date string for display in New York timezone
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
export function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    timeZone: 'America/New_York',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Format a date string for short display (date only) in New York timezone
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
export function formatDateShort(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    timeZone: 'America/New_York',
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

/**
 * Convert a datetime-local input value to ISO string for API
 * @param {string} dateTimeLocal - Date string from datetime-local input
 * @returns {string} ISO date string
 */
export function dateTimeLocalToISO(dateTimeLocal) {
  if (!dateTimeLocal) return '';
  
  // Create date assuming it's in New York timezone
  const date = new Date(dateTimeLocal);
  
  // Get the timezone offset for New York
  const nyDate = new Date(date.toLocaleString("en-US", {timeZone: "America/New_York"}));
  const utcDate = new Date(date.toLocaleString("en-US", {timeZone: "UTC"}));
  const offset = utcDate.getTime() - nyDate.getTime();
  
  // Apply the offset to get the correct UTC time
  const correctedDate = new Date(date.getTime() + offset);
  
  return correctedDate.toISOString();
} 