/**
 * 根据生日计算年龄
 * @param birthday 生日字符串，格式：YYYY-MM-DD
 * @returns 年龄（整数）
 */
export function calculateAge(birthday: string): number {
  if (!birthday) return 0;
  
  const birthDate = new Date(birthday);
  const today = new Date();
  
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  
  // 如果今年的生日还没到，年龄减1
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  
  return age;
}

/**
 * 格式化日期显示
 * @param dateString 日期字符串，格式：YYYY-MM-DD
 * @returns 格式化后的日期字符串
 */
export function formatDate(dateString: string): string {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
}

/**
 * 获取当前日期，格式：YYYY-MM-DD
 * @returns 当前日期字符串
 */
export function getTodayString(): string {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
}

/**
 * 获取最小允许的出生日期（假设最大年龄为120岁）
 * @returns 最小日期字符串，格式：YYYY-MM-DD
 */
export function getMinBirthDate(): string {
  const date = new Date();
  date.setFullYear(date.getFullYear() - 120);
  return formatDate(date.toISOString().split('T')[0]);
}

/**
 * 获取最大允许的出生日期（假设最小年龄为13岁）
 * @returns 最大日期字符串，格式：YYYY-MM-DD
 */
export function getMaxBirthDate(): string {
  const date = new Date();
  date.setFullYear(date.getFullYear() - 13);
  return formatDate(date.toISOString().split('T')[0]);
}

