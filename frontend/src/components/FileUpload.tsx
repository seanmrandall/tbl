import React, { useCallback, useState } from 'react';
import {
  Box,
  Button,
  Text,
  VStack,
  useToast,
  Progress,
  HStack,
  Icon,
} from '@chakra-ui/react';
import { FiUpload, FiFile } from 'react-icons/fi';
import { uploadDataset } from '../services/api';
import { UploadResponse } from '../types/api';

interface FileUploadProps {
  onUploadSuccess: (response: UploadResponse) => void;
  onUploadError: (error: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess, onUploadError }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const toast = useToast();

  const validateFile = (file: File): boolean => {
    if (file.size > 1024 * 1024 * 1024) {
      toast({
        title: 'File too large',
        description: 'File size must be less than 1GB',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return false;
    }

    if (!file.name.toLowerCase().endsWith('.csv')) {
      toast({
        title: 'Invalid file type',
        description: 'Only CSV files are supported',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return false;
    }

    return true;
  };

  const handleFileUpload = async (file: File) => {
    if (!validateFile(file)) return;

    setIsUploading(true);
    setUploadProgress(0);
    setSelectedFile(file);

    try {
      const response = await uploadDataset(file);
      
      toast({
        title: 'Upload successful',
        description: `Dataset uploaded with ${response.row_count} rows`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      onUploadSuccess(response);
    } catch (error: any) {
      toast({
        title: 'Upload failed',
        description: error.message || 'An error occurred during upload',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      onUploadError(error.message || 'Upload failed');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      setSelectedFile(null);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      handleFileUpload(file);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  return (
    <VStack spacing={4} w="full">
      <Box
        w="full"
        h="200px"
        border="2px dashed"
        borderColor={isDragActive ? 'blue.400' : 'gray.300'}
        borderRadius="lg"
        display="flex"
        alignItems="center"
        justifyContent="center"
        bg={isDragActive ? 'blue.50' : 'gray.50'}
        onDragEnter={() => setIsDragActive(true)}
        onDragLeave={() => setIsDragActive(false)}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        cursor="pointer"
        _hover={{ borderColor: 'blue.400', bg: 'blue.50' }}
      >
        <VStack spacing={3}>
          <Icon as={FiUpload} w={8} h={8} color="gray.400" />
          <Text fontSize="lg" color="gray.600" textAlign="center">
            {isDragActive
              ? 'Drop your CSV file here'
              : 'Drag and drop a CSV file here, or click to select'}
          </Text>
          <Text fontSize="sm" color="gray.500" textAlign="center">
            Maximum file size: 1GB
          </Text>
        </VStack>
      </Box>

      <HStack spacing={4}>
        <Button
          as="label"
          htmlFor="file-upload"
          colorScheme="blue"
          leftIcon={<FiFile />}
          isLoading={isUploading}
          loadingText="Uploading..."
          cursor="pointer"
        >
          Select CSV File
        </Button>
        <input
          id="file-upload"
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={isUploading}
        />
      </HStack>

      {selectedFile && (
        <VStack spacing={2} w="full">
          <Text fontSize="sm" color="gray.600">
            Uploading: {selectedFile.name}
          </Text>
          <Progress
            value={uploadProgress}
            w="full"
            colorScheme="blue"
            size="sm"
            borderRadius="md"
          />
        </VStack>
      )}
    </VStack>
  );
};

export default FileUpload; 