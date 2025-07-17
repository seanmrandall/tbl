import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  useToast,
  Flex,
  Heading,
  Input,
  InputGroup,
  InputLeftElement,
  IconButton,
  useColorModeValue,
  Badge,
  Switch,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
import { FiPlay, FiUpload, FiDatabase } from 'react-icons/fi';
import { uploadDataset, getSchema, executeQuery } from './services/api';
import { SchemaResponse, QueryResponse } from './types/api';
import VariableSidebar from './components/VariableSidebar';
import ResultsTable from './components/ResultsTable';
import axios from 'axios';

interface QueryHistoryItem {
  command: string;
  result: QueryResponse | null;
  timestamp: Date;
  error?: string;
}

const App: React.FC = () => {
  const [datasetKey, setDatasetKey] = useState<string | null>(null);
  const [schema, setSchema] = useState<SchemaResponse | null>(null);
  const [query, setQuery] = useState<string>('');
  const [queryHistory, setQueryHistory] = useState<QueryHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isQueryLoading, setIsQueryLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [privacyMode, setPrivacyMode] = useState<'suppression' | 'differential_privacy'>('suppression');
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  // Color scheme
  const bgColor = useColorModeValue('white', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const accentColor = 'blue.500';

  const handleFileUpload = async (file: File, delimiter: string = 'comma') => {
    setIsLoading(true);
    try {
      const uploadResponse = await uploadDataset(file, delimiter);
      setDatasetKey(uploadResponse.dataset_key);
      
      // Get schema after upload
      const schemaResponse = await getSchema(uploadResponse.dataset_key);
      setSchema(schemaResponse);
      setShowUpload(false);
      
      toast({
        title: 'Dataset loaded',
        description: `${uploadResponse.row_count} rows, ${uploadResponse.column_count} columns`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error: any) {
      toast({
        title: 'Upload failed',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadDemoDataset = async () => {
    setIsDemoLoading(true);
    try {
      const response = await axios.post('/api/load-demo/');
      const { dataset_key, row_count, column_count } = response.data;
      setDatasetKey(dataset_key);
      // Get schema after loading demo
      const schemaResponse = await getSchema(dataset_key);
      setSchema(schemaResponse);
      setShowUpload(false);
      toast({
        title: 'Demo dataset loaded',
        description: `${row_count} rows, ${column_count} columns`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error: any) {
      toast({
        title: 'Failed to load demo dataset',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsDemoLoading(false);
    }
  };

  const handleQueryExecution = async (command: string = query) => {
    if (!datasetKey || !command.trim()) {
      toast({
        title: 'Enter a command',
        description: 'Type a Stata-style command and press Enter',
        status: 'warning',
        duration: 2000,
        isClosable: true,
      });
      return;
    }

    const trimmedCommand = command.trim();
    setIsQueryLoading(true);
    
    // Add command to history immediately
    const historyItem: QueryHistoryItem = {
      command: trimmedCommand,
      result: null,
      timestamp: new Date(),
    };
    setQueryHistory(prev => [...prev, historyItem]);

    try {
      console.log('Sending query with privacy mode:', privacyMode);
      const response = await executeQuery({
        dataset_key: datasetKey,
        command: trimmedCommand,
        privacy_mode: privacyMode,
      });
      
      // Update the history item with result
      setQueryHistory(prev => 
        prev.map((item, index) => 
          index === prev.length - 1 
            ? { ...item, result: response }
            : item
        )
      );
    } catch (error: any) {
      // Update the history item with error
      setQueryHistory(prev => 
        prev.map((item, index) => 
          index === prev.length - 1 
            ? { ...item, error: error.message }
            : item
        )
      );
    } finally {
      setIsQueryLoading(false);
      setQuery('');
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQueryExecution();
    }
  };

  // Auto-scroll to bottom when new results are added
  useEffect(() => {
    if (resultsRef.current) {
      resultsRef.current.scrollTop = resultsRef.current.scrollHeight;
    }
  }, [queryHistory]);

  const handleVariableClick = (variableName: string) => {
    setQuery(prev => {
      if (prev.includes('tab ')) {
        return prev.replace(/tab (\w+)(\s|$)/, `tab $1 ${variableName}$2`);
      } else {
        return `tab ${variableName}`;
      }
    });
    inputRef.current?.focus();
  };

  return (
    <Box h="100vh" bg={bgColor} fontFamily="Inter, system-ui, sans-serif">
      {/* Header */}
      <Box 
        borderBottom="1px" 
        borderColor={borderColor} 
        bg="white" 
        px={6} 
        py={4}
        boxShadow="0 1px 3px rgba(0,0,0,0.1)"
      >
        <Flex align="center" justify="space-between">
          <HStack spacing={4}>
            <FiDatabase size={24} color="#3182ce" />
            <Box>
              <Heading size="md" fontWeight="600" color="gray.800">
                Privacy-Preserving Query Interface
              </Heading>
              <Text fontSize="sm" color="gray.600" mt={-1}>
                Stata-style interface for safe frequency tables
              </Text>
            </Box>
          </HStack>
          
          {datasetKey && (
            <HStack spacing={4}>
              <Badge colorScheme="green" variant="subtle">
                Dataset loaded
              </Badge>
              
              {/* Privacy Mode Toggle */}
              <FormControl display="flex" alignItems="center" w="auto">
                <FormLabel htmlFor="privacy-mode" mb="0" fontSize="sm" color="gray.600">
                  {privacyMode === 'suppression' ? 'Suppression' : 'Differential Privacy'}
                </FormLabel>
                <Switch
                  id="privacy-mode"
                  isChecked={privacyMode === 'differential_privacy'}
                  onChange={(e) => {
                    const newMode = e.target.checked ? 'differential_privacy' : 'suppression';
                    console.log('Privacy mode changed to:', newMode);
                    setPrivacyMode(newMode);
                  }}
                  colorScheme="blue"
                  size="sm"
                />
              </FormControl>
              
              <Button
                size="sm"
                variant="ghost"
                leftIcon={<FiUpload />}
                onClick={() => setShowUpload(true)}
              >
                Change Dataset
              </Button>
            </HStack>
          )}
        </Flex>
      </Box>

      <Flex h="calc(100vh - 80px)">
        {/* Variables Sidebar */}
        {schema && !showUpload && datasetKey && (
          <Box
            w="280px"
            borderRight="1px"
            borderColor={borderColor}
            bg="gray.50"
            overflowY="auto"
          >
            <VariableSidebar
              columns={schema.columns}
              onVariableClick={handleVariableClick}
            />
          </Box>
        )}

        {/* Main Content */}
        <Flex flex={1} direction="column">
          {showUpload || !datasetKey ? (
            // Split Upload/Demo Interface
            <Flex p={8} maxW="900px" mx="auto" w="full" gap={8}>
              {/* Upload Your Data */}
              <Box flex={1} p={8} borderRadius="lg" boxShadow="md" bg="white" border="1px solid" borderColor={borderColor}>
                <VStack spacing={6} align="stretch">
                  <Box textAlign="center">
                    <Heading size="md" mb={2}>Upload Your Data</Heading>
                    <Text color="gray.600">Upload a CSV or TSV file to begin analysis</Text>
                  </Box>
                  <VStack spacing={4}>
                    <HStack spacing={4} justify="center">
                      <Text fontSize="sm" fontWeight="500">Delimiter:</Text>
                      <select 
                        id="delimiter-select"
                        style={{
                          padding: '6px 12px',
                          borderRadius: '6px',
                          border: '1px solid #e2e8f0',
                          fontSize: '14px',
                          backgroundColor: 'white'
                        }}
                      >
                        <option value="comma">Comma (,)</option>
                        <option value="tab">Tab</option>
                      </select>
                    </HStack>
                    <Box
                      border="2px dashed"
                      borderColor="gray.300"
                      borderRadius="12px"
                      p={8}
                      textAlign="center"
                      bg="gray.50"
                      _hover={{ borderColor: accentColor, bg: 'blue.50' }}
                      transition="all 0.2s"
                    >
                      <VStack spacing={4}>
                        <FiUpload size={32} color="#718096" />
                        <Text fontSize="lg" fontWeight="500">Drop file here or click to browse</Text>
                        <Button
                          as="label"
                          htmlFor="file-upload"
                          colorScheme="blue"
                          isLoading={isLoading}
                          loadingText="Uploading..."
                          size="lg"
                        >
                          Select File
                        </Button>
                        <input
                          id="file-upload"
                          type="file"
                          accept=".csv,.txt"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) {
                              const delimiter = (document.getElementById('delimiter-select') as HTMLSelectElement).value;
                              handleFileUpload(file, delimiter);
                            }
                          }}
                          style={{ display: 'none' }}
                        />
                      </VStack>
                    </Box>
                  </VStack>
                </VStack>
              </Box>
              {/* Use Demo Dataset */}
              <Box flex={1} p={8} borderRadius="lg" boxShadow="md" bg="gray.50" border="1px solid" borderColor={borderColor} display="flex" flexDirection="column" alignItems="center" justifyContent="center">
                <VStack spacing={6} align="center">
                  <Box textAlign="center">
                    <Heading size="md" mb={2}>Use Demo Dataset</Heading>
                    <Text color="gray.600">Try the app instantly with a synthetic injuries dataset (100,000 rows, tab-delimited)</Text>
                  </Box>
                  <Button
                    colorScheme="teal"
                    size="lg"
                    leftIcon={<FiDatabase />}
                    isLoading={isDemoLoading}
                    loadingText="Loading..."
                    onClick={handleLoadDemoDataset}
                  >
                    Use Demo Dataset
                  </Button>
                </VStack>
              </Box>
            </Flex>
          ) : (
            // Query Interface - REPL Style
            <Flex direction="column" h="full">
                {/* Results History */}
                <Box ref={resultsRef} flex={1} overflowY="auto" p={4}>
                  <VStack spacing={3} align="stretch">
                    {queryHistory.map((item, index) => (
                      <Box key={index}>
                        {/* Command */}
                        <Box 
                          mb={2}
                          fontFamily="'Fira Code', 'Monaco', 'Consolas', monospace"
                          fontSize="14px"
                          color="gray.700"
                        >
                          <Text fontWeight="500" color="blue.600">. {item.command}</Text>
                        </Box>
                        
                        {/* Result or Error */}
                        <Box mb={4}>
                          {item.error ? (
                            <Text color="red.600" fontSize="sm" fontFamily="'Fira Code', 'Monaco', 'Consolas', monospace">
                              {item.error}
                            </Text>
                          ) : item.result ? (
                            <ResultsTable result={item.result} />
                          ) : (
                            <Text color="gray.500" fontSize="sm">Executing...</Text>
                          )}
                        </Box>
                      </Box>
                    ))}
                    
                    {queryHistory.length === 0 && (
                      <Box textAlign="center" py={12} color="gray.500">
                        <Text fontSize="lg" mb={2}>Ready to analyze</Text>
                        <Text fontSize="sm">Type a command and press Enter to begin</Text>
                      </Box>
                    )}
                  </VStack>
                </Box>

                {/* Command Input - Fixed at Bottom */}
                <Box 
                  borderTop="1px" 
                  borderColor={borderColor} 
                  p={4} 
                  bg="white"
                  boxShadow="0 -1px 3px rgba(0,0,0,0.1)"
                >
                  <InputGroup size="lg">
                    <InputLeftElement pointerEvents="none">
                      <Text color="gray.400" fontSize="sm" fontWeight="500">&gt;</Text>
                    </InputLeftElement>
                    <Input
                      ref={inputRef}
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Enter Stata-style command (e.g., tab sex age if region == 'Rural')"
                      fontFamily="'Fira Code', 'Monaco', 'Consolas', monospace"
                      fontSize="14px"
                      border="1px"
                      borderColor="gray.300"
                      borderRadius="8px"
                      _focus={{ 
                        borderColor: 'blue.400', 
                        boxShadow: '0 0 0 1px #3182ce' 
                      }}
                      _placeholder={{ color: 'gray.400' }}
                    />
                    <IconButton
                      aria-label="Execute query"
                      icon={<FiPlay />}
                      colorScheme="blue"
                      onClick={() => handleQueryExecution()}
                      isLoading={isQueryLoading}
                      size="lg"
                      borderLeftRadius={0}
                      borderRightRadius="8px"
                    />
                  </InputGroup>
                </Box>
              </Flex>
            )}
        </Flex>
      </Flex>
    </Box>
  );
};

export default App; 