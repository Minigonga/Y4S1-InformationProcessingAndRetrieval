// Configuration
const API_BASE_URL = 'http://localhost:5000';

// DOM elements
const searchForm = document.getElementById('searchForm');
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const rowsSelect = document.getElementById('rowsSelect');
const searchModeSelect = document.getElementById('searchMode');
const modeDescription = document.getElementById('modeDescription');
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const searchInfoDiv = document.getElementById('searchInfo');

// Filter elements
const toggleFiltersBtn = document.getElementById('toggleFilters');
const filtersContainer = document.getElementById('filtersContainer');
const priceFilter = document.getElementById('priceFilter');
const yearFilter = document.getElementById('yearFilter');
const ageFilter = document.getElementById('ageFilter');
const osFilter = document.getElementById('osFilter');
const playtimeFilter = document.getElementById('playtimeFilter');
const clearFiltersBtn = document.getElementById('clearFilters');

// Store all results for client-side filtering
let allResults = [];

// Search mode descriptions
const modeDescriptions = {
    'keyword': 'Traditional keyword-based search using BM25 ranking',
    'semantic': 'AI-powered semantic search understanding meaning and context',
    'hybrid': 'Combined approach using both keyword matching and semantic understanding'
};

// Event listeners
searchForm.addEventListener('submit', handleSearch);
searchModeSelect.addEventListener('change', updateModeDescription);
toggleFiltersBtn.addEventListener('click', toggleFilters);
clearFiltersBtn.addEventListener('click', clearFilters);
priceFilter.addEventListener('change', applyFilters);
yearFilter.addEventListener('change', applyFilters);
ageFilter.addEventListener('change', applyFilters);
osFilter.addEventListener('change', applyFilters);
playtimeFilter.addEventListener('change', applyFilters);

// Update mode description when selection changes
function updateModeDescription() {
    const mode = searchModeSelect.value;
    modeDescription.textContent = modeDescriptions[mode];
}

// Toggle filters visibility
function toggleFilters() {
    const isVisible = filtersContainer.style.display !== 'none';
    filtersContainer.style.display = isVisible ? 'none' : 'block';
    toggleFiltersBtn.textContent = isVisible ? '🎛️ Show Filters' : '🎛️ Hide Filters';
}

// Debounce function for input filtering
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Clear all filters
function clearFilters() {
    priceFilter.selectedIndex = 0;
    yearFilter.selectedIndex = 0;
    ageFilter.selectedIndex = 0;
    osFilter.selectedIndex = 0;
    playtimeFilter.selectedIndex = 0;
    applyFilters();
}

// Apply filters to results
function applyFilters() {
    if (allResults.length === 0) return;
    
    const priceLabel = priceFilter.value;
    const yearLabel = yearFilter.value;
    const ageLabel = ageFilter.value;
    const osLabel = osFilter.value;
    const playtimeLabel = playtimeFilter.value;
    
    const filtered = allResults.filter(doc => {
        // Price label filter
        if (priceLabel && doc.price_range_label !== priceLabel) return false;
        
        // Release year label filter
        if (yearLabel && doc.release_year_label !== yearLabel) return false;
        
        // Age rating filter
        if (ageLabel) {
            const docAges = Array.isArray(doc.age_rating_label) ? doc.age_rating_label : [doc.age_rating_label];
            if (!docAges.includes(ageLabel)) return false;
        }
        
        // OS filter
        if (osLabel) {
            const docOS = Array.isArray(doc.OS_label) ? doc.OS_label : [doc.OS_label];
            if (!docOS.includes(osLabel)) return false;
        }
        
        // Playtime label filter
        if (playtimeLabel && doc.playtime_label !== playtimeLabel) return false;
        
        return true;
    });
    
    displayResults(filtered, filtered.length, 0, searchModeSelect.value);
}

// Handle search form submission
async function handleSearch(e) {
    e.preventDefault();
    
    const query = searchInput.value.trim();
    const rows = parseInt(rowsSelect.value);
    const mode = searchModeSelect.value;
    
    if (!query) {
        showError('Please enter a search query');
        return;
    }
    
    // Clear previous results and errors
    resultsDiv.innerHTML = '';
    errorDiv.style.display = 'none';
    searchInfoDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                rows: rows,
                mode: mode
            })
        });
        
        const data = await response.json();
        
        loadingDiv.style.display = 'none';
        
        if (data.success) {
            displayResults(data.results, data.numFound, data.qtime, data.mode);
        } else {
            showError(data.error || 'An error occurred while searching');
        }
        
    } catch (error) {
        loadingDiv.style.display = 'none';
        showError('Network error: ' + error.message);
    }
}

// Display search results
function displayResults(results, numFound, qtime, mode) {
    // Store results for filtering (only if it's a fresh search, not filtered results)
    if (qtime > 0) {
        allResults = results;
    }
    
    if (results.length === 0) {
        resultsDiv.innerHTML = `
            <div style="text-align: center; padding: 40px; background: white; border-radius: 8px;">
                <h3>No results found</h3>
                <p style="color: #666; margin-top: 10px;">Try different keywords or adjust your filters</p>
            </div>
        `;
        searchInfoDiv.style.display = 'block';
        searchInfoDiv.innerHTML = 'No results match your criteria';
        return;
    }
    
    // Show search info
    searchInfoDiv.style.display = 'block';
    const modeLabel = mode === 'keyword' ? 'Keyword' : mode === 'semantic' ? 'Semantic' : 'Hybrid';
    const timeInfo = qtime > 0 ? ` in <strong>${qtime}ms</strong>` : '';
    searchInfoDiv.innerHTML = `
        Found <strong>${numFound}</strong> results${timeInfo} using <strong>${modeLabel}</strong> search
    `;
    
    // Display results
    resultsDiv.innerHTML = results.map((doc, index) => createResultCard(doc, index, mode)).join('');
}

// Create a result card HTML
function createResultCard(doc, index, mode) {
    const title = doc.title || 'Untitled';
    const description = doc.about_the_game || doc.detailed_description || 'No description available';
    const imageUrl = doc.header_image || 'https://via.placeholder.com/460x215?text=No+Image';
    const releaseDate = doc.release_date ? new Date(doc.release_date).toLocaleDateString() : 'Unknown';
    const price = doc.price ? `$${parseFloat(doc.price).toFixed(2)}` : 'Free';
    const developers = doc.developers ? (Array.isArray(doc.developers) ? doc.developers.join(', ') : doc.developers) : 'Unknown';
    const genres = doc.genres || [];
    const categories = doc.categories || [];
    const tags = doc.tags || [];
    const achievements = doc.achievements || 0;
    
    // Truncate description
    const truncatedDesc = truncateText(stripHtml(description), 200);
    
    // Combine genres, categories, and first few tags
    const allTags = [...genres, ...categories, ...tags.slice(0, 3)];
    const uniqueTags = [...new Set(allTags)].slice(0, 8);
    
    // Build score display based on search mode
    let scoreDisplay = '';
    if (mode === 'semantic' && doc.semantic_score !== undefined) {
        scoreDisplay = `<span class="score-badge semantic">Similarity: ${(doc.semantic_score * 100).toFixed(1)}%</span>`;
    } else if (mode === 'hybrid' && doc.hybrid_score !== undefined) {
        scoreDisplay = `
            <span class="score-badge hybrid">Hybrid: ${(doc.hybrid_score * 100).toFixed(1)}%</span>
            <span class="score-badge-small">KW: ${(doc.keyword_score * 100).toFixed(0)}% | Sem: ${(doc.semantic_score * 100).toFixed(0)}%</span>
        `;
    } else if (doc.score !== undefined) {
        scoreDisplay = `<span class="score-badge keyword">Score: ${doc.score.toFixed(2)}</span>`;
    }
    
    return `
        <div class="result-item" onclick="window.location.href='/game/${doc.id}'" style="cursor: pointer;">
            <div class="result-header">
                <div class="result-image">
                    <img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(title)}" onerror="this.src='https://via.placeholder.com/460x215?text=No+Image'">
                </div>
                <div class="result-info">
                    <h2 class="result-title">
                        ${escapeHtml(title)}
                        ${scoreDisplay}
                    </h2>
                    <div class="result-meta">
                        <span class="meta-item">📅 ${escapeHtml(releaseDate)}</span>
                        <span class="meta-item">💰 ${escapeHtml(price)}</span>
                        ${achievements ? `<span class="meta-item">🏆 ${achievements} achievements</span>` : ''}
                        ${developers !== 'Unknown' ? `<span class="meta-item">👨‍💻 ${escapeHtml(developers)}</span>` : ''}
                    </div>
                </div>
            </div>
            
            <div class="result-description">
                ${escapeHtml(truncatedDesc)}
            </div>
            
            ${uniqueTags.length ? `
                <div class="result-tags">
                    ${uniqueTags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}
            
            <div class="result-footer">
                Document ID: ${doc.id}
                <span style="float: right; color: #4a90e2;">Click for details →</span>
            </div>
        </div>
    `;
}

// Helper function to strip HTML tags
function stripHtml(html) {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
}

// Helper function to truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

// Helper function to escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Show error message
function showError(message) {
    errorDiv.style.display = 'block';
    errorDiv.innerHTML = `<strong>Error:</strong> ${escapeHtml(message)}`;
}

// Handle enter key in search input
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        handleSearch(e);
    }
});
