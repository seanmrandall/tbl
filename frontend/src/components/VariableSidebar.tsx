import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Divider,
  Heading,
} from '@chakra-ui/react';
import { Column } from '../types/api';

interface VariableSidebarProps {
  columns: Column[];
  onVariableClick?: (columnName: string) => void;
}

const VariableSidebar: React.FC<VariableSidebarProps> = ({ 
  columns, 
  onVariableClick 
}) => {
  return (
    <Box p={4}>
      <VStack spacing={4} align="stretch">
        <Box>
          <Heading size="sm" color="gray.700" mb={1}>
            Variables
          </Heading>
          <Text fontSize="xs" color="gray.500">
            {columns.length} total
          </Text>
        </Box>

        <VStack spacing={2} align="stretch">
          {columns.map((column) => (
            <Box
              key={column.name}
              p={3}
              bg="white"
              borderRadius="6px"
              border="1px"
              borderColor="gray.200"
              cursor={onVariableClick ? 'pointer' : 'default'}
              _hover={onVariableClick ? { 
                bg: column.type === 'string' ? 'blue.50' : 'green.50', 
                borderColor: column.type === 'string' ? 'blue.300' : 'green.300',
                transform: 'translateY(-1px)',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              } : {}}
              onClick={() => onVariableClick?.(column.name)}
              transition="all 0.2s"
            >
              <HStack justify="space-between" align="center">
                <Text fontSize="sm" fontWeight="500" color="gray.800">
                  {column.name}
                </Text>
                <Badge 
                  size="sm" 
                  colorScheme={column.type === 'string' ? 'blue' : 'green'} 
                  variant="subtle"
                >
                  {column.type}
                </Badge>
              </HStack>
            </Box>
          ))}
        </VStack>
      </VStack>
    </Box>
  );
};

export default VariableSidebar; 