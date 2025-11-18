// 设置 CSS 变量以匹配视口的实际高度
export default function setAppHeight() {
    const doc = document.documentElement;
    doc.style.setProperty('--app-height', `${window.innerHeight}px`);
}
