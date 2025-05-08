// INF_2900_TEAM5/library_manager/frontend/tests/performance/dataProcessing.test.js

// Mock a data processing function (e.g., sorting a large array)
function simulateDataProcessing(arraySize = 10000) {
    const arr = Array.from({ length: arraySize }, () => Math.random());
    arr.sort((a, b) => a - b);
    return arr.length; // Return something
}

test('simulated data processing time for large array', () => {
    const startTime = performance.now();
    simulateDataProcessing(50000); // Process a larger array
    const endTime = performance.now();
    const processingTime = endTime - startTime;

    console.log(`Simulated data processing time (large array): ${processingTime.toFixed(2)} ms`);
    // Example: Expect processing time to be less than 150 milliseconds
    expect(processingTime).toBeLessThan(150);
});

test('simulated data processing time for small array', () => {
    const startTime = performance.now();
    simulateDataProcessing(100); // Process a smaller array
    const endTime = performance.now();
    const processingTime = endTime - startTime;

    console.log(`Simulated data processing time (small array): ${processingTime.toFixed(2)} ms`);
    // Expect very fast execution
    expect(processingTime).toBeLessThan(10);
});