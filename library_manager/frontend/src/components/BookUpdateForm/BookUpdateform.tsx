const updateBook = async (bookId: number, updatedData: Partial<Book>) => {
    try {
        const response = await fetch(`/api/update_book/${bookId}/`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updatedData),
        });

        if (!response.ok) {
            throw new Error("Failed to update book");
        }

        const result = await response.json();
        alert(result.message);
        refreshBookList(); // Refresh UI with updated books
    } catch (error) {
        console.error("Error updating book:", error);
    }
};

