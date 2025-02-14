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
        
        ${recipe.image_name ? `
            <div class="mb-6">
                <img src="/Food Images/Food Images/${recipe.image_name}" 
                     alt="${recipe.title}"
                     class="w-full rounded-lg shadow-md object-cover h-96"
                     onerror="this.style.display='none'"
                />
            </div>
        ` : ''}
        
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
    
    showLoading();
    recipeList.innerHTML = '';

    try {
        const response = await fetch(`http://127.0.0.1:8000/recipes/search?ingredient=${encodeURIComponent(ingredients)}`);
        
        if (!response.ok) {
            throw new Error('No recipes found for these ingredients');
        }

        const data = await response.json();
        const recipes = data.items;

        if (recipes.length === 0) {
            recipeList.innerHTML = `
                <div class="col-span-full text-center py-8 text-gray-600">
                    No recipes found for these ingredients. Try different combinations!
                </div>
            `;
        } else {
            recipes.forEach(recipe => {
                const recipeCard = document.createElement('div');
                recipeCard.className = 'bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2';
                recipeCard.innerHTML = `
                    ${recipe.image_name ? `
                        <div class="w-full h-48 overflow-hidden">
                            <img src="/Food Images/Food Images/${recipe.image_name}" 
                                 alt="${recipe.title}"
                                 class="w-full h-full object-cover transform hover:scale-110 transition-transform duration-500"
                                 onerror="this.style.display='none'"
                            />
                        </div>
                    ` : ''}
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
                recipeList.appendChild(recipeCard);
            });
        }
    } catch (error) {
        recipeList.innerHTML = `
            <div class="col-span-full text-center text-red-600 py-4">
                ${error.message}
            </div>
        `;
    } finally {
        hideLoading();
    }
});


recipeModal.addEventListener('click', function(event) {
    if (event.target === recipeModal) {
        closeModal();
    }
});