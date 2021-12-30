/**
 * @file bolb下载工具
 * 文件下载工具函数，自动添加下载dom元素并执行下载。
 * @param {Object} blobData 下载内容的数据流bolb对象
 * @param {string} fileName 下载文件保存名称
 */

export function downloadBlobFile(blobData, fileName) {
    const blob = new Blob([blobData]);
    const downloadElement = document.createElement('a');
    const href = window.URL.createObjectURL(blob);
    downloadElement.href = href;
    downloadElement.download = fileName;
    document.body.appendChild(downloadElement);
    downloadElement.click();
    document.body.removeChild(downloadElement);
    window.URL.revokeObjectURL(href);
}
