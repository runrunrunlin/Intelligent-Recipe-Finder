const recipeModal = document.getElementById('recipe-modal');
const modalContent = document.getElementById('modal-content');
const loadingElement = document.getElementById('loading');

function showLoading() {
    loadingElement.classList.remove('hidden');
}

function hideLoading() {
    loadingElement.classList.add('hidden');
}

function closeModal() {
    recipeModal.classList.add('hidden');
}

function showRecipeDetails(recipe) {
    modalContent.innerHTML = `
        <h2 class="text-2xl font-bold mb-4">${recipe.title}</h2>
        
        <div class="mb-6">
            <h3 class="text-lg font-semibold mb-2">Ingredients</h3>
            <p class="text-gray-600">${recipe.ingredients_text}</p>
        </div>
        
        ${recipe.instructions ? `
            <div class="mb-6">
                <h3 class="text-lg font-semibold mb-2">Instructions</h3>
                <div class="space-y-2">
                    ${recipe.instructions.split('\n').map((step, index) => `
                        <div class="flex gap-3">
                            <span class="font-medium text-gray-400">${index + 1}.</span>
                            <p class="text-gray-700">${step}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
    recipeModal.classList.remove('hidden');
}

document.getElementById('ingredient-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const ingredients = document.getElementById('ingredients').value.trim();
    const recipeList = document.getElementById('recipe-list');

    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.classList.remove('hidden');
    }
    
    recipeList.innerHTML = '';
    recipeList.classList.remove('hidden');
    
    console.log("Searching ingredients:", ingredients); // Debug log

    try {
        const response = await fetch(`/recipes/search?ingredient=${encodeURIComponent(ingredients)}`);

        console.log("API response status:", response.status); // Debug log
        
        if (!response.ok) {
            throw new Error (`Search error: ${response.status}`);
        }

        const data = await response.json();

        console.log("Search results:", data); // Debug log
        
        const recipes = data.items;

        if (recipes.length === 0) {
            recipeList.innerHTML = `
                <div class="col-span-full text-center py-8 text-gray-600">
                    No recipes found for these ingredients. Try different combinations!
                </div>
            `;
        } else {

            const gridContainer = document.createElement('div');
            gridContainer.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6';
            recipeList.appendChild(gridContainer);

            recipes.forEach(recipe => {
                const recipeCard = document.createElement('div');
                recipeCard.className = 'bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2';
                recipeCard.innerHTML = `
                    <div class="p-6">
                        <div class="flex justify-between items-start mb-4">
                            <h3 class="text-xl font-bold text-gray-800">${recipe.title}</h3>
                            <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                                ${recipe.cleaned_ingredients ? recipe.cleaned_ingredients.length : '0'} Ingredients
                            </span>
                        </div>
                        
                        <div class="space-y-4">
                            <div class="text-sm text-gray-500">Ingredients:</div>
                            <p class="text-gray-600 line-clamp-2">${recipe.ingredients_text}</p>
                            
                            ${recipe.cleaned_ingredients ? `
                                <div class="flex flex-wrap gap-2">
                                    ${recipe.cleaned_ingredients.slice(0, 3).map(ingredient => `
                                        <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                                            ${ingredient}
                                        </span>
                                    `).join('')}
                                    ${recipe.cleaned_ingredients.length > 3 ? `
                                        <span class="text-xs text-gray-500">
                                            +${recipe.cleaned_ingredients.length - 3} more
                                        </span>
                                    ` : ''}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
                recipeCard.addEventListener('click', () => showRecipeDetails(recipe));
                gridContainer.appendChild(recipeCard);  
            });
        }
    } catch (error) {
        console.error("Search error:", error);
        recipeList.innerHTML = `
            <div class="col-span-full text-center text-red-600 py-4">
                ${error.message}
            </div>
        `;
    } finally {
        if (loadingElement) {
            loadingElement.classList.add('hidden');
        }
    }
});


recipeModal.addEventListener('click', function(event) {
    if (event.target === recipeModal) {
        closeModal();
    }
});