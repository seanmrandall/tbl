import React from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Text,
  Badge,
  VStack,
  HStack,
} from '@chakra-ui/react';
import { QueryResponse } from '../types/api';

interface ResultsTableProps {
  result: QueryResponse | null;
  isLoading?: boolean;
}

const ResultsTable: React.FC<ResultsTableProps> = ({ result, isLoading = false }) => {
  if (isLoading) {
    return (
      <Text color="gray.500" fontSize="sm">Executing...</Text>
    );
  }

  if (!result) {
    return null;
  }

  if (result.data.length === 0) {
    return (
      <Text color="gray.500" fontSize="sm">
        {result.message || 'No data matches the specified conditions'}
      </Text>
    );
  }

  const isSuppressed = (value: any): boolean => {
    return value === '<5' || value === 'nan' || value === null;
  };

  // Check if any values are suppressed
  const hasSuppressedValues = result.data.some(row => 
    row.some(cell => isSuppressed(cell))
  );
  
  // Debug logging for suppression check
  console.log('Suppression check:', {
    hasSuppressedValues,
    dataLength: result.data.length,
    sampleData: result.data.slice(0, 3),
    sampleSuppressed: result.data.slice(0, 3).map(row => row.map(cell => isSuppressed(cell)))
  });

  // Check if this is a two-way table (3 columns: var1, var2, count)
  const isTwoWayTable = result.columns.length === 3 && 
    (result.columns[2] === 'count' || result.columns[2] === 'Count' || 
     result.columns[2] === 'N' || result.columns[2] === 'n' ||
     result.columns[2] === 'frequency' || result.columns[2] === 'Frequency' ||
     result.columns[2] === 'freq');
  
  // Debug logging
  console.log('Result columns:', result.columns);
  console.log('Result data sample:', result.data.slice(0, 3));
  console.log('Is two-way table:', isTwoWayTable);

  if (isTwoWayTable) {
    return <TwoWayTable result={result} isSuppressed={isSuppressed} />;
  }

  return (
    <VStack spacing={3} align="start" w="auto">
      <HStack justify="space-between" fontSize="xs" color="gray.600" w="full">
        <Text>{result.row_count} rows in filtered dataset</Text>
        <Badge colorScheme="blue" size="sm" variant="subtle">
          {result.data.length} result rows
        </Badge>
      </HStack>

      <Box
        border="1px"
        borderColor="gray.200"
        borderRadius="6px"
        overflow="hidden"
        maxH="400px"
        overflowY="auto"
        w="auto"
        minW="fit-content"
      >
        <Table variant="simple" size="sm" w="auto">
          <Thead bg="gray.50" position="sticky" top={0}>
            <Tr>
              {result.columns.map((column, index) => (
                <Th key={index} py={2} fontSize="xs" fontWeight="600" whiteSpace="nowrap">
                  {column}
                </Th>
              ))}
            </Tr>
          </Thead>
          <Tbody>
            {result.data.map((row, rowIndex) => (
              <Tr key={rowIndex} _hover={{ bg: 'gray.50' }}>
                {row.map((cell, cellIndex) => (
                  <Td key={cellIndex} py={1} fontSize="xs" whiteSpace="nowrap">
                    {isSuppressed(cell) ? (
                      <Badge colorScheme="red" size="sm" variant="subtle">
                        {cell}
                      </Badge>
                    ) : (
                      <Text>{cell}</Text>
                    )}
                  </Td>
                ))}
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>

      {hasSuppressedValues && (
        <Box p={2} bg="blue.50" borderRadius="4px" w="full">
          <Text fontSize="xs" color="blue.700">
            <strong>Note:</strong> Values marked with <Badge colorScheme="red" size="sm" variant="subtle">{"<5"}</Badge> have been suppressed for privacy protection.
          </Text>
        </Box>
      )}
    </VStack>
  );
};

// Component for displaying two-way tables in cross-tabulation format
const TwoWayTable: React.FC<{ result: QueryResponse; isSuppressed: (value: any) => boolean }> = ({ 
  result, 
  isSuppressed 
}) => {
  const [var1, var2, countCol] = result.columns;
  
  console.log('TwoWayTable - Processing data:', {
    var1, var2, countCol,
    dataLength: result.data.length,
    sampleData: result.data.slice(0, 3)
  });
  
  // Get unique values for each variable
  const var1Values = [...new Set(result.data.map(row => row[0]))].sort();
  const var2Values = [...new Set(result.data.map(row => row[1]))].sort();
  
  console.log('Unique values:', { var1Values, var2Values });
  
  // Create a map for quick lookup
  const dataMap = new Map();
  result.data.forEach(row => {
    dataMap.set(`${row[0]}|${row[1]}`, row[2]);
  });

  // Calculate totals
  const rowTotals = var1Values.map(v1 => 
    var2Values.reduce((sum, v2) => {
      const val = dataMap.get(`${v1}|${v2}`);
      return sum + (isSuppressed(val) ? 0 : (Number(val) || 0));
    }, 0)
  );
  
  const colTotals = var2Values.map(v2 => 
    var1Values.reduce((sum, v1) => {
      const val = dataMap.get(`${v1}|${v2}`);
      return sum + (isSuppressed(val) ? 0 : (Number(val) || 0));
    }, 0)
  );
  
  const grandTotal = rowTotals.reduce((sum, total) => sum + total, 0);

  // Check if any values are suppressed in the two-way table
  const hasSuppressedValues = result.data.some(row => isSuppressed(row[2]));
  
  // Debug logging for two-way table suppression check
  console.log('TwoWayTable suppression check:', {
    hasSuppressedValues,
    dataLength: result.data.length,
    sampleData: result.data.slice(0, 3),
    sampleSuppressed: result.data.slice(0, 3).map(row => isSuppressed(row[2]))
  });

  return (
    <VStack spacing={3} align="start" w="auto">
      <HStack justify="space-between" fontSize="xs" color="gray.600" w="full">
        <Text>Cross-tabulation: {var1} × {var2}</Text>
        <Badge colorScheme="green" size="sm" variant="subtle">
          {var1Values.length} × {var2Values.length} cells
        </Badge>
      </HStack>

      <Box
        border="1px"
        borderColor="gray.200"
        borderRadius="6px"
        overflow="hidden"
        maxH="400px"
        overflowY="auto"
        w="auto"
        minW="fit-content"
      >
        <Table variant="simple" size="sm" w="auto">
          <Thead bg="gray.50" position="sticky" top={0}>
            <Tr>
              <Th py={2} fontSize="xs" fontWeight="600" borderRight="1px" borderColor="gray.300" whiteSpace="nowrap">
                {var1} \ {var2}
              </Th>
              {var2Values.map((value, index) => (
                <Th key={index} py={2} fontSize="xs" fontWeight="600" textAlign="center" whiteSpace="nowrap">
                  {value}
                </Th>
              ))}
              <Th py={2} fontSize="xs" fontWeight="600" textAlign="center" bg="gray.100" borderLeft="1px" borderColor="gray.300" whiteSpace="nowrap">
                Total
              </Th>
            </Tr>
          </Thead>
          <Tbody>
            {var1Values.map((v1, rowIndex) => (
              <Tr key={rowIndex} _hover={{ bg: 'gray.50' }}>
                <Td py={1} fontSize="xs" fontWeight="500" borderRight="1px" borderColor="gray.300" whiteSpace="nowrap">
                  {v1}
                </Td>
                {var2Values.map((v2, colIndex) => {
                  const value = dataMap.get(`${v1}|${v2}`);
                  return (
                    <Td key={colIndex} py={1} fontSize="xs" textAlign="center" whiteSpace="nowrap">
                      {isSuppressed(value) ? (
                        <Badge colorScheme="red" size="sm" variant="subtle">
                          {value}
                        </Badge>
                      ) : (
                        <Text>{value}</Text>
                      )}
                    </Td>
                  );
                })}
                <Td py={1} fontSize="xs" fontWeight="500" textAlign="center" bg="gray.100" borderLeft="1px" borderColor="gray.300" whiteSpace="nowrap">
                  {rowTotals[rowIndex]}
                </Td>
              </Tr>
            ))}
            <Tr bg="gray.100" borderTop="2px" borderColor="gray.300">
              <Td py={1} fontSize="xs" fontWeight="600" borderRight="1px" borderColor="gray.300" whiteSpace="nowrap">
                Total
              </Td>
              {colTotals.map((total, index) => (
                <Td key={index} py={1} fontSize="xs" fontWeight="600" textAlign="center" whiteSpace="nowrap">
                  {total}
                </Td>
              ))}
              <Td py={1} fontSize="xs" fontWeight="600" textAlign="center" bg="gray.200" borderLeft="1px" borderColor="gray.300" whiteSpace="nowrap">
                {grandTotal}
              </Td>
            </Tr>
          </Tbody>
        </Table>
      </Box>

      {hasSuppressedValues && (
        <Box p={2} bg="blue.50" borderRadius="4px" w="full">
          <Text fontSize="xs" color="blue.700">
            <strong>Note:</strong> Values marked with <Badge colorScheme="red" size="sm" variant="subtle">{"<5"}</Badge> have been suppressed for privacy protection.
          </Text>
        </Box>
      )}
    </VStack>
  );
};

export default ResultsTable; 