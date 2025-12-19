import React, { useState } from 'react';
import { 
  Download, 
  ExternalLink, 
  Maximize2, 
  X, 
  Copy,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import './ImageGallery.css';

function ImageGallery({ images, title, onDownload }) {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imageErrors, setImageErrors] = useState({});

  const handleImageError = (imageId, error) => {
    console.error(`Image ${imageId} failed to load:`, error);
    setImageErrors(prev => ({ ...prev, [imageId]: true }));
  };

  const handleImageLoad = (imageId) => {
    setImageErrors(prev => ({ ...prev, [imageId]: false }));
  };

  const copyUrlToClipboard = async (url) => {
    try {
      await navigator.clipboard.writeText(url);
      toast.success('Image URL copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy URL');
    }
  };

  const openInNewTab = (url) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const getProxiedUrl = (url) => {
    if (!url) return null;
    
    // If it's a local API URL, use it directly
    if (url.startsWith('/api/')) {
      return `http://localhost:8000${url}`;
    }
    
    // If it's an external URL, use proxy to avoid CORS issues
    if (url.startsWith('http')) {
      return `http://localhost:8000/api/proxy-image?url=${encodeURIComponent(url)}`;
    }
    
    return url;
  };

  const isImageUrl = (url) => {
    if (!url) return false;
    if (url.includes('fal.media') || url.includes('fal.ai') || url.includes('storage.googleapis.com')) return true;
    if (url.includes('.png') || url.includes('.jpg') || url.includes('.jpeg')) return true;
    if (url.startsWith('https://') && !url.endsWith('.json')) return true;
    return false;
  };

  if (!images || images.length === 0) {
    return (
      <div className="image-gallery empty">
        <div className="empty-state">
          <div className="empty-icon">🖼️</div>
          <h3>No Images Generated</h3>
          <p>Generate frames to see them here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="image-gallery">
      {title && <h3 className="gallery-title">{title}</h3>}
      
      <div className="gallery-grid">
        {images.map((image, index) => {
          const imageId = `${image.id || index}`;
          const hasError = imageErrors[imageId];
          const isImage = isImageUrl(image.url);
          
          return (
            <div key={imageId} className="gallery-item">
              <div className="image-container">
                {isImage && !hasError ? (
                  <>
                    <img
                      src={getProxiedUrl(image.url)}
                      alt={image.title || `Generated frame ${index + 1}`}
                      className="gallery-image"
                      onLoad={() => handleImageLoad(imageId)}
                      onError={(e) => handleImageError(imageId, e)}
                      onClick={() => setSelectedImage(image)}
                    />
                    <div className="image-overlay">
                      <button
                        className="overlay-btn"
                        onClick={() => setSelectedImage(image)}
                        title="View full size"
                      >
                        <Maximize2 size={16} />
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="image-placeholder">
                    {hasError ? (
                      <>
                        <AlertCircle size={32} />
                        <span>Failed to load</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle size={32} />
                        <span>Ready</span>
                      </>
                    )}
                  </div>
                )}
              </div>
              
              <div className="image-info">
                <div className="image-title">
                  {image.title || `Frame ${index + 1}`}
                </div>
                <div className="image-meta">
                  {image.cached && <span className="cache-badge">cached</span>}
                  {image.generationTime && (
                    <span className="time-badge">{image.generationTime}s</span>
                  )}
                </div>
                <div className="image-actions">
                  <button
                    className="action-btn"
                    onClick={() => copyUrlToClipboard(image.url)}
                    title="Copy URL"
                  >
                    <Copy size={14} />
                  </button>
                  <button
                    className="action-btn"
                    onClick={() => openInNewTab(image.url)}
                    title="Open in new tab"
                  >
                    <ExternalLink size={14} />
                  </button>
                  <button
                    className="action-btn download-btn"
                    onClick={() => onDownload && onDownload(image.url, image.filename || `frame_${index + 1}.png`)}
                    title="Download"
                  >
                    <Download size={14} />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Full-size modal */}
      {selectedImage && (
        <div className="image-modal" onClick={() => setSelectedImage(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedImage.title || 'Generated Frame'}</h3>
              <button
                className="close-btn"
                onClick={() => setSelectedImage(null)}
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="modal-image-container">
              <img
                src={getProxiedUrl(selectedImage.url)}
                alt={selectedImage.title || 'Generated frame'}
                className="modal-image"
              />
            </div>
            
            <div className="modal-actions">
              <button
                className="modal-action-btn"
                onClick={() => copyUrlToClipboard(selectedImage.url)}
              >
                <Copy size={16} />
                Copy URL
              </button>
              <button
                className="modal-action-btn"
                onClick={() => openInNewTab(selectedImage.url)}
              >
                <ExternalLink size={16} />
                Open Original
              </button>
              <button
                className="modal-action-btn download-btn"
                onClick={() => {
                  onDownload && onDownload(
                    selectedImage.url, 
                    selectedImage.filename || 'generated_frame.png'
                  );
                  setSelectedImage(null);
                }}
              >
                <Download size={16} />
                Download
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ImageGallery;